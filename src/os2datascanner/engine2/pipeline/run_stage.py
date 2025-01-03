import os
import sys
import click
import pstats
import random
import structlog
from collections import deque

from prometheus_client import Info, Summary, start_http_server, CollectorRegistry

from os2datascanner.utils import debug, profiling
from ... import __version__
from ..model.core import SourceManager
from . import explorer, exporter, matcher, messages, processor, tagger, worker
from .utilities.pika import (ANON_QUEUE,
                             RejectMessage,
                             PikaPipelineThread,
                             HandleMessageType)

logger = structlog.get_logger("run_stage")


_module_mapping = {
    "explorer": explorer,
    "processor": processor,
    "matcher": matcher,
    "tagger": tagger,
    "exporter": exporter,
    "worker": worker
}


def _compatibility_main(stage):
    print("{0}: warning: this command is deprecated,"
          " use run_stage.py instead".format(sys.argv[0]))
    sys.argv = [sys.argv[0], stage]
    main()


def restart_process():
    """Clean exit, used to release all ressources used by this process and children.

    Restart will be handled by kubernetes or docker, depending on the setup."""
    sys.exit(0)


class GenericRunner(PikaPipelineThread):
    def __init__(self,
                 source_manager: SourceManager, *args,
                 stage: str, module,  limit, queue_priorities, **kwargs):
        super().__init__(*args, **kwargs,
                         read=tuple(set(module.READS_QUEUES).union(set(queue_priorities))),
                         write=module.WRITES_QUEUES,
                         prefetch_count=module.PREFETCH_COUNT)
        self._module = module
        self._registry = CollectorRegistry()
        self._summary = Summary(
                f"os2datascanner_pipeline_{stage}",
                self._module.PROMETHEUS_DESCRIPTION,
                registry=self._registry)
        self._source_manager = source_manager

        self._stage = stage

        self._cancelled = deque()

        self._limit = limit
        self._count = 0

        self._queue_priorities = queue_priorities
        if self._queue_priorities:
            logger.info(
                "Running with queue prioritization",
                queue_priorities=self._queue_priorities)
            self._first_priority = self._queue_priorities[0]  # First entry, first prio.
            self._current_priority = None
            self._consumer_tags = {}

    def make_channel(self):
        channel = super().make_channel()

        # Declare an anonymous queue and bind it to the fanout exchange; we
        # use this to receive command messages
        anon_queue = channel.queue_declare(
                ANON_QUEUE,
                passive=False, durable=False, exclusive=False,
                auto_delete=True, arguments={"x-max-priority": 10})
        channel.queue_bind(
                exchange="broadcast", queue=anon_queue.method.queue)
        return channel

    def _basic_consume(self, *, exclusive=False):
        consumer_tags = super()._basic_consume(exclusive=exclusive)
        consumer_tags["anon"] = self.channel.basic_consume(
                ANON_QUEUE, self.handle_message_raw, exclusive=False)
        self._consumer_tags = consumer_tags

        return consumer_tags

    def handle_message_raw(self, channel, method, properties, body):
        if self._stage in ("worker", "explorer",):
            self._check_and_switch_priority()

        super().handle_message_raw(channel, method, properties, body)

    def _check_and_switch_priority(self):  # noqa CCR001, cognitive complexity (17 > 15)
        """Switch consumers dynamically based on queue message counts."""
        queue_msg_counts = {
            queue: self.channel.queue_declare(queue=queue, passive=True).method.message_count
            for queue in self._queue_priorities
        }

        first_priority_count = queue_msg_counts[self._first_priority]

        # Match on the state of the first-priority queue and the current priority
        match (first_priority_count, self._current_priority):
            case (count, current) if count > 0 and current != self._first_priority:
                # First priority queue has messages: cancel lower-priority consumers
                logger.info("Switching to first priority", first_priority=self._first_priority)
                for queue in self._queue_priorities:
                    if queue != self._first_priority and queue in self._consumer_tags:
                        logger.info("Cancelling consumer", queue=queue)
                        self.channel.basic_cancel(self._consumer_tags.pop(queue))
                self._current_priority = self._first_priority

            case (0, current) if current == self._first_priority:
                # First priority is empty and currently active: check lower-priority queues
                for queue in self._queue_priorities:
                    if queue == self._first_priority:
                        continue  # Skip first priority
                    # If the queue has no consumer and messages, start one
                    if queue not in self._consumer_tags and queue_msg_counts[queue] > 0:
                        logger.info("Starting consumer", queue=queue)
                        self._consumer_tags[queue] = self.channel.basic_consume(
                            queue=queue,
                            on_message_callback=self.handle_message_raw,
                            exclusive=False
                        )
                        self._current_priority = queue
                        break  # Break the loop - we don't want to start any more consumers.

                # Cancel other lower-priority consumers
                for queue in self._queue_priorities:
                    if queue not in self._consumer_tags or queue == self._first_priority:
                        continue

                    if self._current_priority != queue:
                        logger.info("Cancelling low prio consumer", queue=queue)
                        self.channel.basic_cancel(self._consumer_tags.pop(queue))

            case _:
                # No action needed
                logger.debug("No priority switch necessary.")

    def _handle_command(self, routing_key, body):
        command = messages.CommandMessage.from_json_object(body)

        if command.abort:
            self._cancelled.appendleft(command.abort)

        if command.profiling is not None:
            profiling.print_stats(pstats.SortKey.CUMULATIVE, silent=True)
            if command.profiling:
                profiling.enable_profiling()
                logger.info("enabling profiling")
            else:
                profiling.disable_profiling()
                logger.info("disabling profiling")

        yield from []

    def _handle_content(self, routing_key, body):
        raw_scan_tag = body.get("scan_tag")

        if not raw_scan_tag and "scan_spec" in body:
            raw_scan_tag = body["scan_spec"]["scan_tag"]

        if raw_scan_tag:
            scan_tag = messages.ScanTagFragment.from_json_object(raw_scan_tag)

            if scan_tag in self._cancelled:
                logger.debug(
                        f"scan {raw_scan_tag} is cancelled, "
                        "ignoring")
                raise RejectMessage(requeue=False)

        yield from self._module.message_received_raw(
                body, routing_key, self._source_manager)

    def handle_message(self, routing_key, body) -> HandleMessageType:
        with self._summary.time():
            logger.debug(f"{routing_key}: {str(body)}")
            if routing_key == "":
                yield from self._handle_command(routing_key, body)
            else:
                yield from self._handle_content(routing_key, body)

    def after_message(self, routing_key, body):
        # Check to see if we've met our quota and should restart
        self._count += 1
        if self._limit is not None and self._count >= self._limit:
            global restarting
            restarting = True
            self.enqueue_stop()


restarting = False


@click.command()
@click.option('--profile/--no-profile', 'enable_profiling',
              default=False, envvar='ENABLE_PROFILING',
              is_flag=True, help='record and print profiling output')
@click.option('--rusage/--no-rusage', 'enable_rusage',
              default=False, envvar='ENABLE_RUSAGE',
              is_flag=True,
              help='print resource usage statistics on exit or SIGUSR1')
@click.option('--enable-metrics/--disable-metrics', 'enable_metrics',
              default=False, envvar='EXPORT_METRICS',
              help='enable exporting of metrics')
@click.option('--prometheus-port', default=9091,
              type=int, envvar='PROMETHEUS_PORT',
              help='the port to serve OpenMetrics data.')
@click.option('--width', default=3,
              type=int, envvar='WIDTH',
              help='allow each source to have at most SIZE simultaneous open sub-sources')
@click.option('--single-cpu', type=int,
              envvar='SCHEDULE_ON_CPU',
              help='instruct the scheduler to run this stage, and its'
                   ' subprocesses, on the CPU with the given (wrapped)'
                   ' index')
@click.option('--restart-after', default=None,
              envvar='RESTART_AFTER', type=int,
              help='re-execute this stage after it has handled COUNT messages (default: None)')
@click.argument('stage',
                type=click.Choice(["explorer",
                                   "processor",
                                   "matcher",
                                   "tagger",
                                   "exporter",
                                   "worker"]))
@click.option("--queue-priority", envvar='QUEUE_PRIORITY',
              multiple=True, type=str,
              help='queue priorities, can be multiple: first entry equals highest priority.')
def main(enable_profiling, enable_rusage, enable_metrics,
         prometheus_port, width, single_cpu, restart_after, stage,
         queue_priority):
    debug.register_debug_signal()
    module = _module_mapping[stage]
    logger.info("starting pipeline", stage=stage)

    if enable_rusage:
        debug.add_debug_function(debug.rusage_dbg_func)

    if enable_metrics:
        i = Info(f"os2datascanner_pipeline_{stage}", "version number")
        i.info({"version": __version__})
        start_http_server(prometheus_port)

    if single_cpu:
        available_cpus = sorted(os.sched_getaffinity(0))
        if seq_id := single_cpu:
            # If we've been assigned to a specific processor, then use that
            # (modulo the number of actually available CPUs, so we can safely
            # use an instance counter as a processor selector)
            cpu = available_cpus[int(seq_id) % len(available_cpus)]
        else:
            # Otherwise, pick a random CPU to run on
            cpu = random.choice(available_cpus)
        logger.info(f"executing only on CPU {cpu}")
        os.sched_setaffinity(0, {cpu})

    if enable_profiling:
        logger.info("enabling profiling")
        profiling.enable_profiling()

    try:
        with SourceManager(width=width) as source_manager:
            GenericRunner(
                source_manager,
                stage=stage,
                module=module,
                limit=restart_after,
                queue_priorities=queue_priority).run_consumer()

        if restarting:
            logger.info(f"restarting after {restart_after} messages")
            restart_process()
    finally:
        profiling.print_stats(pstats.SortKey.CUMULATIVE, silent=True)

        if enable_rusage:
            debug.rusage_dbg_func(None, None)


if __name__ == "__main__":
    main()
