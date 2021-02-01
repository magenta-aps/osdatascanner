from os import getpid

from prometheus_client import start_http_server

from ..rules.rule import Rule
from ..conversions.types import decode_dict
from . import messages
from .utilities.args import AppendReplaceAction, make_common_argument_parser
from .utilities.pika import PikaPipelineRunner
from .utilities.systemd import notify_ready, notify_stopping
from .utilities.prometheus import prometheus_summary


def message_received_raw(body, channel, source_manager):
    source_manager = None
    message = messages.RepresentationMessage.from_json_object(body)
    representations = decode_dict(message.representations)
    rule = message.progress.rule

    new_matches = []

    # Keep executing rules for as long as we can with the representations we
    # have
    while not isinstance(rule, bool):
        head, pve, nve = rule.split()

        target_type = head.operates_on
        type_value = target_type.value
        if type_value not in representations:
            # We don't have this representation -- bail out
            break
        representation = representations[type_value]

        matches = list(head.match(representation))
        new_matches.append(
                messages.MatchFragment(head, matches or None))
        if matches:
            rule = pve
        else:
            rule = nve

    final_matches = message.progress.matches + new_matches

    if isinstance(rule, bool):
        # We've come to a conclusion!
        for matches_q in ("os2ds_matches", "os2ds_checkups",):
            yield (matches_q,
                    messages.MatchesMessage(
                            message.scan_spec, message.handle,
                            rule, final_matches).to_json_object())
        # Only trigger metadata scanning if the match succeeded
        if rule:
            yield ("os2ds_handles",
                    messages.HandleMessage(
                            message.scan_spec.scan_tag,
                            message.handle).to_json_object())
    else:
        # We need a new representation to continue
        yield ("os2ds_conversions",
                messages.ConversionMessage(
                        message.scan_spec, message.handle,
                        message.progress._replace(
                                rule=rule,
                                matches=final_matches)).to_json_object())


def main():
    parser = make_common_argument_parser()
    parser.description = ("Consume representations and generate matches"
            + " and fresh conversions.")

    args = parser.parse_args()

    if args.enable_metrics:
        start_http_server(args.prometheus_port)


    class MatcherRunner(PikaPipelineRunner):
        @prometheus_summary(
                "os2datascanner_pipeline_matcher", "Representations examined")
        def handle_message(self, body, *, channel=None):
            if args.debug:
                print(channel, body)
            return message_received_raw(body, channel, None)

    with MatcherRunner(
            read=["os2ds_representations"],
            write=["os2ds_handles",
                    "os2ds_matches", "os2ds_checkups", "os2ds_conversions"],
            heartbeat=6000) as runner:
        try:
            print("Start")
            notify_ready()
            runner.run_consumer()
        finally:
            print("Stop")
            notify_stopping()


if __name__ == "__main__":
    main()
