# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from . import messages


READS_QUEUES = ("os2ds_matches", "os2ds_metadata", "os2ds_problems",)
WRITES_QUEUES = ("os2ds_results",)
PROMETHEUS_DESCRIPTION = "Messages exported"
PREFETCH_COUNT = 8


def censor_outgoing_message(message):
    """Censors a message before sending it to the outside world."""
    if isinstance(message, messages.MetadataMessage):
        return messages.replace(message, handle=message.handle.censor())
    elif isinstance(message, messages.MatchesMessage):
        return messages.replace(message,
                                handle=message.handle.censor(),
                                scan_spec=censor_outgoing_message(message.scan_spec))
    elif isinstance(message, messages.ProblemMessage):
        return messages.replace(message,
                                handle=message.handle.censor() if message.handle else None,
                                source=message.source.censor() if message.source else None)

    # Not exported from the pipeline, but included here for completeness
    elif isinstance(message, messages.ScanSpecMessage):
        return messages.replace(message, source=message.source.censor())
    elif isinstance(message, (
            messages.ConversionMessage, messages.RepresentationMessage)):
        return messages.replace(message,
                                handle=message.handle.censor(),
                                scan_spec=censor_outgoing_message(message.scan_spec))
    elif isinstance(message, messages.HandleMessage):
        return messages.replace(message, handle=message.handle.censor())
    else:
        return message


def message_received_raw(body, channel, source_manager):
    body["origin"] = channel

    message = None
    if "metadata" in body:
        message = messages.MetadataMessage.from_json_object(body)
    elif "matched" in body:
        message = messages.MatchesMessage.from_json_object(body)
    elif "message" in body:
        message = messages.ProblemMessage.from_json_object(body)
    # Old-style problem messages are now ignored

    if message:
        result_body = censor_outgoing_message(message).to_json_object()
        result_body["origin"] = channel

        yield ("os2ds_results", result_body)


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("exporter")
