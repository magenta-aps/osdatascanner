# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import gzip
import json
from typing import override

import pika
import pika.exceptions
import click
import pstats
import random
import importlib
import structlog
from collections import deque

from prometheus_client import Info, Summary, start_http_server, CollectorRegistry

from os2datascanner.utils import debug, profiling
from ... import __version__
from .. import settings
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
                 stage: str, module,  limit, queue_priorities,
                 conversion_priority: tuple[str, ...] = (), **kwargs):
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

        # Scan tags that have been cancelled. Appended by _dispatch_command
        # (background thread), checked by _handle_content (main thread).
        self._cancelled = deque()

        self._limit = limit
        self._count = 0

        # Pending queue subscriptions: appended by _dispatch_command (background
        # thread, under self._condition), drained by _processing_complete
        # (background thread, under self._condition).
        self._pending_new_queues: list[tuple[str, str]] = []
        # Background-thread-only state (no locking needed):
        self._per_scan_queue_priorities: dict[str, str] = {}
        self._conversion_priority = conversion_priority

        # Delivery counts per queue, incremented by handle_message_raw and
        # snapshot-and-cleared by _check_per_scan_priority. Both run on the
        # background thread.
        self._delivery_counts: dict[str, int] = {}

        self._queue_priorities = queue_priorities
        if self._queue_priorities:
            logger.info(
                "Running with queue prioritization",
                queue_priorities=self._queue_priorities)
            self._first_priority = self._queue_priorities[0]  # First entry, first prio.
            self._current_priority = None
            # Background-thread-only: maps queue name to pika consumer tag.
            # Mutated by _dispatch_command, _processing_complete,
            # _subscribe_to_queue, _basic_consume, and tick hooks.
            self._consumer_tags = {}

    @override
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
        # Remember the queue name so we can include it in the worker_hello
        # message. The status_collector uses it to reply directly to us
        # instead of re-broadcasting to consumer in the system.
        self._anon_queue_name = anon_queue.method.queue
        return channel

    @override
    def _basic_consume(self, *, exclusive=False):
        # Drop all per-scan queue subscriptions before (re-)subscribing.
        # make_channel() declares every queue in self._read with passive=False,
        # so any per-scan queues left in _read after a deletion would be silently
        # re-created as zombies. Clearing them here ensures make_channel() only
        # touches the static-named queues.
        # The worker_hello broadcast below lets the status_collector re-send any currently
        # active per-scan queues, and the worker re-subscribes to them via
        # new_queue_hook with passive=True.
        for q in list(self._per_scan_queue_priorities):
            self._read.discard(q)
        self._per_scan_queue_priorities.clear()

        consumer_tags = super()._basic_consume(exclusive=exclusive)
        # Register the anon queue with auto_ack=True so that abort and other
        # command messages are delivered regardless of the data channel's prefetch
        # state. Prefetch limits only apply to unacked messages; auto-acked
        # consumers are immune. Commands are handled entirely in handle_message_raw
        # (background thread) and never reach the main thread's _incoming queue.
        consumer_tags["anon"] = self.channel.basic_consume(
                ANON_QUEUE, self.handle_message_raw, exclusive=False, auto_ack=True)
        self._consumer_tags = consumer_tags

        if hasattr(self._module, "basic_consume_hook"):
            self._module.basic_consume_hook(self)

        return consumer_tags

    def _dispatch_command(self, cmd):  # noqa: CCR001
        """(Background thread.) Executes a parsed CommandMessage immediately.

        Called from handle_message_raw for messages received on the auto-acked
        anon queue consumer, so every action here is guaranteed to run even
        when the data channel's prefetch slots are fully exhausted."""
        if cmd.abort:
            # Notify the in-progress worker immediately so it can stop
            # between pages/items without waiting for the main thread.
            logger.info("abort command received in background thread", scan_tag=cmd.abort)
            self._cancelled.appendleft(cmd.abort)
            if hasattr(self._module, "notify_abort"):
                self._module.notify_abort(cmd.abort)

        if cmd.delete_queue and cmd.delete_queue in self._consumer_tags:
            # Update tracking state immediately so the rest of the system sees
            # this queue as gone. We intentionally do NOT call basic_cancel
            # here: the broker is about to delete the queue and will send its
            # own basic.cancel. If we race and send basic_cancel after the
            # broker already did, the broker returns channel error 404
            # (consumer not found), which closes the channel. The
            # ConsumerCancelled handler in _processing_complete cleans up.
            self._forget_queue(cmd.delete_queue)

            logger.info(
                    "Pre-emptively untracked consumer for deleted queue",
                    queue=cmd.delete_queue)

        if cmd.new_queue:
            # Signal _processing_complete to subscribe to the new queue.
            with self._condition:
                tag = cmd.new_queue_priority or ""
                self._pending_new_queues.append((cmd.new_queue, tag))

        if cmd.profiling is not None:
            profiling.print_stats(pstats.SortKey.CUMULATIVE, silent=True)
            if cmd.profiling:
                profiling.enable_profiling()
                logger.info("enabling profiling")
            else:
                profiling.disable_profiling()
                logger.info("disabling profiling")

    @override
    def handle_message_raw(self, channel, method, properties, body):
        """(Background thread.) Handles all incoming AMQP messages.

        Command messages arrive via the auto-acked anon queue consumer and are
        dispatched to _dispatch_command entirely here, without involving the
        main thread. Commands arrive on two routing keys: "" (fanout broadcast
        to all workers) and the anon queue name itself (direct response from
        the status_collector to this specific worker, e.g. new_queue after a
        worker_hello). Both are auto-acked, so they must never flow through
        _incoming and the normal enqueue_ack path. Manually acking an
        already-acked message causes a 406 PRECONDITION_FAILED that closes the
        channel. Handling both here guarantees they are always processed
        regardless of the data channel's prefetch state.

        Data messages are passed to the parent, which enqueues them in
        _incoming for the main thread to process."""
        anon_queue = getattr(self, "_anon_queue_name", None)
        is_command = body and (
                method.routing_key == ""
                or method.routing_key == anon_queue)
        if is_command:
            try:
                raw = gzip.decompress(body) if getattr(
                        properties, "content_encoding", None) == "gzip" else body
                self._dispatch_command(
                        messages.CommandMessage.from_json_object(json.loads(raw)))
            except Exception:
                logger.warning("Couldn't parse command message! Discarding and moving on..")
                pass  # Parsing failed; log a warning and discard silently

            # Command messages are auto-acked; do not pass to _incoming.
            # Putting them there would cause run_consumer to call enqueue_ack
            # on an already-acked delivery tag, which closes the channel.
            return

        # Track deliveries per queue for priority decisions
        queue = method.routing_key
        if queue in self._per_scan_queue_priorities:
            self._delivery_counts[queue] = self._delivery_counts.get(queue, 0) + 1

        super().handle_message_raw(channel, method, properties, body)

    def _subscribe_to_queue(self, queue_name: str, tag: str = ""):
        """(Background thread.) Subscribe to a new per-scan conversion queue."""
        if queue_name in self._read:
            # We're already there.
            return

        self._read.add(queue_name)
        self._per_scan_queue_priorities[queue_name] = tag
        try:
            # passive=True: only subscribe if the queue already exists.
            # The scan may have completed and the queue deleted between the
            # broadcast arriving and us processing it. Using passive=False here
            # would silently re-create the queue as an empty zombie.
            self.channel.queue_declare(queue_name, passive=True)
        except Exception:
            # Queue is gone. Undo state additions before re-raising so that
            # the channel recovery path (_basic_consume) doesn't try to
            # resubscribe to a queue that no longer exists.
            self._read.discard(queue_name)
            self._per_scan_queue_priorities.pop(queue_name, None)
            logger.warning("Per-scan queue gone before subscription, skipping",
                           queue=queue_name)
            raise

        consumer_tag = self.channel.basic_consume(
                queue_name, self.handle_message_raw, exclusive=False)
        self._consumer_tags[queue_name] = consumer_tag
        logger.info("Subscribed to per-scan queue", queue=queue_name, tag=tag)

    @override
    def _processing_complete(self, tick):
        # This is run between deliveries of messages. In the callback handle_message_raw,
        # that may call _dispatch_command, we record intent, f.e. to subscribe to a new queue, but
        # wait to do so, until here, where it's safe to do so.
        # I.e., we can't mutate a channel in delivery callback, so we sort that out here.
        with self._condition:
            new_queues = self._pending_new_queues[:]
            del self._pending_new_queues[:]

        for queue_name, priority in new_queues:
            if hasattr(self._module, "new_queue_hook"):
                self._module.new_queue_hook(self, queue_name, priority)
        try:
            result = super()._processing_complete(tick)
        except pika.exceptions.ConsumerCancelled as e:
            # Broker cancelled a consumer because the per-scan queue was deleted
            # before our proactive cancel in handle_message_raw could run (race
            # between the delete_queue broadcast and the actual queue deletion).
            # Clean up and keep running; no reason to crash over a cancelled scan.
            cancelled_tag = e.args[0] if e.args else None

            dead = next(
                (q for q, tag in self._consumer_tags.items() if tag == cancelled_tag),
                None)
            if dead:
                self._forget_queue(dead)
            logger.warning(
                "Consumer cancelled by broker; cleaned up and continuing",
                consumer_tag=cancelled_tag, dead_queue=dead)
            result = None

        if tick and tick % 50 == 0:
            if hasattr(self._module, "tick_hook"):
                self._module.tick_hook(self)

        return result

    def _forget_queue(self, queue_name: str) -> None:
        """ Forget about this per-scan queue.
        Drop our tracking state."""
        self._consumer_tags.pop(queue_name, None)
        self._per_scan_queue_priorities.pop(queue_name, None)
        self._read.discard(queue_name)

    def _check_and_switch_priority(self):  # noqa CCR001, cognitive complexity (17 > 15)
        """Switch consumers dynamically based on queue message counts."""
        queue_msg_counts = {}
        for queue in self._queue_priorities:
            try:
                queue_msg_counts[queue] = self.channel.queue_declare(
                        queue=queue, passive=True).method.message_count
            except Exception:
                return  # Channel closed by broker (queue missing); bail out

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
                logger.trace("No priority switch necessary.")

    def _check_per_scan_priority(self):
        """For workers with a configured conversion priority: focus on per-scan
        queues whose tag appears earliest in the worker's priority list.

        Uses delivery counts tracked by handle_message_raw instead of polling
        the broker with queue_declare(passive=True).

        A worker with conversion_priority=("delta", "full") focuses on
        delta-scan queues and only helps with full-scan queues when there is
        no delta work left. A worker with conversion_priority=("delta",)
        will never consume full-scan queues."""

        # Snapshot and reset delivery counts since last check
        counts = self._delivery_counts.copy()
        self._delivery_counts.clear()

        # Tags that currently have unprocessed deliveries
        active_tags = {
            qtag for q, qtag in self._per_scan_queue_priorities.items()
            if counts.get(q, 0) > 0
        }

        # Highest-priority tag (earliest in the list) that's active
        active_tag = next(
            (tag for tag in self._conversion_priority if tag in active_tags),
            None)

        for q, qtag in list(self._per_scan_queue_priorities.items()):
            should_consume = (
                    qtag in self._conversion_priority
                    and (active_tag is None or qtag == active_tag)
            )
            has_consumer = q in self._consumer_tags

            # Channel-dead returns bail out the whole pass; next tick retries.
            match (should_consume, has_consumer):
                case (True, False):  # We should consume but aren't
                    try:
                        self._consumer_tags[q] = self.channel.basic_consume(
                            q, self.handle_message_raw, exclusive=False)
                    except Exception:
                        self._forget_queue(q)
                        return
                    logger.info("Subscribed per-scan queue",
                                queue=q, tag=qtag, active_tag=active_tag)
                case (False, True):  # We shouldn't consume but are
                    try:
                        self.channel.basic_cancel(self._consumer_tags.pop(q))
                    except Exception:
                        self._consumer_tags.pop(q, None)
                        return
                    logger.info("Cancelled per-scan queue",
                                queue=q, tag=qtag, active_tag=active_tag)

    def _handle_content(self, routing_key, body):
        raw_scan_tag = body.get("scan_tag")

        if not raw_scan_tag and "scan_spec" in body:
            raw_scan_tag = body["scan_spec"]["scan_tag"]

        scan_tag = None
        if raw_scan_tag:
            scan_tag = messages.ScanTagFragment.from_json_object(raw_scan_tag)
            if scan_tag in self._cancelled:
                logger.debug(
                        f"scan {raw_scan_tag} is cancelled, "
                        "ignoring")
                raise RejectMessage(requeue=False)

        for result in self._module.message_received_raw(
                body, routing_key, self._source_manager):
            if scan_tag and scan_tag in self._cancelled:
                # An abort command arrived while we were mid-processing.
                # Stop yielding results and let the message be acked normally;
                # results already yielded have already been enqueued, so there
                # is no clean way to retract them, but we avoid generating the
                # rest.
                logger.info(
                        "scan cancelled mid-processing, stopping early",
                        scan_tag=raw_scan_tag)
                return
            yield result

    @override
    def handle_message(self, routing_key, body) -> HandleMessageType:
        with self._summary.time():
            logger.debug(f"{routing_key}: {str(body)}")
            # Commands are fully handled by _dispatch_command on the background
            # thread (via handle_message_raw). They should never reach here
            # because handle_message_raw returns early for them. If one somehow
            # does, just ignore it.
            anon_queue = getattr(self, "_anon_queue_name", None)
            if routing_key == "" or routing_key == anon_queue:
                return
            yield from self._handle_content(routing_key, body)

    @override
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
                                   "exporter",
                                   "worker"]))
@click.option("--queue-priority", envvar='QUEUE_PRIORITY',
              multiple=True, type=str,
              help='queue priorities, can be multiple: first entry equals highest priority.')
@click.option("--conversion-priority", envvar='CONVERSION_PRIORITY',
              multiple=True, type=str,
              help='for worker stages: per-scan queue tags in priority order.'
                   ' Workers only consume queues whose tag is in this list.'
                   ' First entry is highest priority. Unset means no filtering.')
def main(enable_profiling, enable_rusage, enable_metrics,
         prometheus_port, width, single_cpu, restart_after, stage,
         queue_priority, conversion_priority):

    for module_name in settings.pipeline.get("extra_modules") or []:
        logger.info(
                "loading additional pipeline module",
                module_name=module_name)
        importlib.import_module(
                module_name,
                package="os2datascanner.engine2")

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
                queue_priorities=queue_priority,
                conversion_priority=conversion_priority).run_consumer()

        if restarting:
            logger.info(f"restarting after {restart_after} messages")
            restart_process()
    finally:
        profiling.print_stats(pstats.SortKey.CUMULATIVE, silent=True)

        if enable_rusage:
            debug.rusage_dbg_func(None, None)


if __name__ == "__main__":
    main()
