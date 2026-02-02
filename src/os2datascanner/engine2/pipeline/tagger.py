from collections.abc import Generator

from os2datascanner.engine2.model.core.utilities import SourceManager
from .. import settings
from ..utilities.backoff import TimeoutRetrier
from . import messages


def message_received(
        message: messages.HandleMessage,
        sm: SourceManager) -> Generator[messages.SerialisableMessage]:
    tr = TimeoutRetrier(
            seconds=settings.pipeline["op_timeout"],
            max_tries=settings.pipeline["op_tries"])

    try:
        resource = message.handle.follow(sm)
        metadata = tr.run(resource.get_metadata)
        yield messages.MetadataMessage(
                message.scan_tag, message.handle, metadata)
    except Exception as e:
        exception_message = (
            "Metadata extraction error. {0}: ".format(type(e).__name__))
        exception_message += ", ".join([str(a) for a in e.args])
        yield messages.ProblemMessage(
                scan_tag=message.scan_tag,
                source=None, handle=message.handle,
                message=exception_message)


def message_received_raw(body, channel, source_manager):
    for m in message_received(
            messages.HandleMessage.from_json_object(body),
            source_manager):
        queue: str | None
        if isinstance(m, messages.MetadataMessage):
            queue = "os2ds_metadata"
        elif isinstance(m, messages.ProblemMessage):
            queue = "os2ds_problems"
        else:
            raise TypeError(type(m))
        if queue:
            yield (queue, m.to_json_object())


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("tagger")
