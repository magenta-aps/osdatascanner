import email
import email.policy
import mimetypes

import extract_msg as _extract_msg
from extract_msg.msg_classes.message_base import MessageBase as _MessageBase

from ..core import Source
from .mail import MailSource

mimetypes.add_type("application/vnd.ms-outlook", ".msg")


class UnsupportedMsgClassError(ValueError):
    pass


def _msg_to_email_message(path: str) -> email.message.EmailMessage:
    """Open a .msg file and return its content as an email.message.EmailMessage."""
    with _extract_msg.openMsg(path) as msg:
        if not isinstance(msg, _MessageBase):
            raise UnsupportedMsgClassError(
                f"{path}: .msg class {msg.classType!r} is not a supported"
                f" email type")
        raw = msg.asEmailMessage().as_bytes()
        return email.message_from_bytes(raw, policy=email.policy.default)


@Source.mime_handler("application/vnd.ms-outlook")
class MsgSource(MailSource):
    """Handles Outlook .msg files by converting them to RFC 822 email
    messages and delegating to MailSource's traversal logic."""
    type_label = "msg"

    def _generate_state(self, sm):
        with self.handle.follow(sm).make_path() as p:
            yield _msg_to_email_message(p)
