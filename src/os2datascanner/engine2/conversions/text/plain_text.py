from ..types import OutputType
from ..registry import conversion


@conversion(OutputType.Text, "text/plain", "text/csv", "application/csv",)
def plain_text_processor(r, **kwargs):
    with r.make_stream() as t:
        try:
            return t.read().decode()
        except UnicodeDecodeError:
            return None
