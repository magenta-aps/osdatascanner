#!/usr/bin/env python3

import sys
import json
import click

from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.exporter import censor_outgoing_message
from os2datascanner.engine2.pipeline.utilities import pika


class_mapping = {
    "os2ds_checkups": messages.MatchesMessage,
    "os2ds_conversions": messages.ConversionMessage,
    "os2ds_handles": messages.HandleMessage,
    "os2ds_matches": messages.MatchesMessage,
    "os2ds_metadata": messages.MetadataMessage,
    "os2ds_problems": messages.ProblemMessage,
    "os2ds_representations": messages.RepresentationMessage,
    "os2ds_scan_specs": messages.ScanSpecMessage,
    "os2ds_status": messages.StatusMessage,
}


class Printer(pika.PikaPipelineThread):
    def __init__(
            self, *args, reject, censor, pretty_print, timeout, **kwargs):
        super().__init__(*args, **kwargs)
        self.reject = reject
        self.censor = censor
        self.pretty_print = pretty_print
        self.timeout = timeout

    def render_json(self, body):
        return json.dumps(body, indent=self.pretty_print or None)

    def handle_message(self, routing_key, body):
        if routing_key == "os2ds_results":
            routing_key = body["origin"]

        message = None
        try:
            if routing_key in class_mapping:
                message = class_mapping[routing_key].from_json_object(body)
        except Exception:
            pass

        if not message:
            if self.censor:
                print(
                        "warning: unrecognised message format,"
                        " printing uncensored content", file=sys.stderr)
            print(self.render_json(body))
        else:
            if self.censor:
                print(
                        "information: message format recognised, printing censored"
                        " content", file=sys.stderr)
                pm = censor_outgoing_message(message)
            else:
                pm = message
            print(self.render_json(pm.to_json_object()))

        if self.reject:
            raise pika.RejectMessage(requeue=False)

        # Enqueueing a stop command before handle_message returns ensures that
        # we'll disconnect before we acknowledge recept of this message
        self.enqueue_stop()
        yield from []

    def after_timeout(self):
        print("Timed out, stopping", file=sys.stderr)
        self.enqueue_stop()
        self.join()

    def after_message(self, routing_key, body, *, ex=None):
        # Presumably we got here because we rejected the message, so let's
        # just stop
        self.enqueue_stop()


@click.command()
@click.option("--reject/--no-reject", "reject",
              default=False,
              is_flag=True, help="reject (discard) the displayed message")
@click.option("--censor/--no-censor", "censor",
              default=True,
              is_flag=True, help="censor the message before displaying it")
@click.option("--pretty-print/--ugly-print", "pretty_print",
              default=True,
              is_flag=True, help="print the message with indentation")
@click.option('--timeout', type=float, default=30.0,
              help='wait for a message for the given number of seconds')
@click.argument("queues", nargs=-1)
def main(
        reject: bool, censor: bool, pretty_print: bool, timeout: float,
        queues: tuple[str, ...]):
    print(f"Waiting for a message on any of {queues}...")
    with Printer(
            read=set(queues),
            reject=reject, censor=censor, pretty_print=pretty_print,
            timeout=timeout) as p:
        p.run_consumer()


if __name__ == '__main__':
    main()
