from typing import Optional
from email.header import decode_header


def decode_encoded_words(k: str) -> str:
    """Decodes a string that might contain Encoded-Word values."""
    result = ""
    for segment, charset in decode_header(k):
        segment_str = None
        if isinstance(segment, str) and charset is None:
            segment_str = segment
        elif isinstance(segment, bytes):
            try:
                segment_str = segment.decode(charset or "ascii")
            except (LookupError, UnicodeDecodeError):
                # The character set of this segment isn't recognised (or was
                # recognised, but is incorrect). Decode it as ASCII and replace
                # unknown bytes with placeholders
                segment_str = segment.decode(
                        encoding="ascii", errors="replace")
        if segment_str:
            result += segment_str
    return result


def get_safe_filename(k: Optional[str]) -> str:
    """Converts a MIME part's filename into a name usable in the local
    filesystem."""

    if not k:
        return "file"

    # Emails seen in the wild occasionally use full URLs as MIME part filenames
    # (what?!), so drop everything before the last "/"
    if "/" in k:
        k = k.rsplit("/", maxsplit=1)[-1]

    return k
