from .. import settings
from ..utilities.backoff import TimeoutRetrier
from . import messages


def message_received_raw(body, channel, source_manager):
    message = messages.HandleMessage.from_json_object(body)

    tr = TimeoutRetrier(
            seconds=settings.pipeline["op_timeout"],
            max_tries=settings.pipeline["op_tries"])

    try:
        resource = message.handle.follow(source_manager)
        metadata = tr.run(resource.get_metadata)
        yield ("os2ds_metadata",
               messages.MetadataMessage(
                        message.scan_tag, message.handle, metadata
                ).to_json_object())
    except Exception as e:
        exception_message = (
            "Metadata extraction error. {0}: ".format(type(e).__name__))
        exception_message += ", ".join([str(a) for a in e.args])
        yield ("os2ds_problems", messages.ProblemMessage(
                scan_tag=message.scan_tag,
                source=None, handle=message.handle,
                message=exception_message).to_json_object())


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("tagger")
