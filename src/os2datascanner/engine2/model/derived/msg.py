import email
import email.policy
import mimetypes

import bs4
import extract_msg as _extract_msg
from extract_msg.msg_classes.message_base import MessageBase as _MessageBase

from ..core import Source
from .mail import MailSource

mimetypes.add_type("application/vnd.ms-outlook", ".msg")


class UnsupportedMsgClassError(ValueError):
    pass


def _ensure_utf8_html_body(msg: _MessageBase) -> None:
    """extract_msg's MessageBase.asEmailMessage() assumes that the raw HTML
    body it reads from the .msg file is UTF-8 encoded, but Outlook can also
    write it out in other encodings (e.g. windows-1252). Detect that case and
    replace the cached body with a UTF-8 re-encoding so asEmailMessage()
    doesn't crash.

    BeautifulSoup is used rather than a plain decode-and-re-encode because it
    also rewrites the HTML's own "charset" meta tag to match, avoiding a
    mismatch that would otherwise garble the text again further down the
    conversion pipeline."""
    html_body = msg.htmlBody
    if not html_body:
        return
    try:
        html_body.decode("utf-8")
    except UnicodeDecodeError:
        soup = bs4.BeautifulSoup(html_body, "html.parser")
        msg.__dict__["htmlBody"] = soup.encode("utf-8")


def _msg_to_email_message(path: str) -> email.message.EmailMessage:
    """Open a .msg file and return its content as an email.message.EmailMessage."""
    with _extract_msg.openMsg(path) as msg:
        if not isinstance(msg, _MessageBase):
            raise UnsupportedMsgClassError(
                f"{path}: .msg class {msg.classType!r} is not a supported"
                f" email type")
        _ensure_utf8_html_body(msg)
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
