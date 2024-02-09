from lxml import html

from ..types import OutputType
from ..registry import conversion


@conversion(OutputType.Text, "text/html")
def html_processor(r, **kwargs):
    with r.make_stream() as fp:
        # This tells lxml to retrieve the page, locate the <body> tag then
        # extract and print all the text.
        try:
            html_body = html.parse(fp).xpath("//body")[0]
            for br in html_body.xpath("//br | //p | //div"):
                br.tail = f"\n {br.tail}" if br.tail else "\n"
            content = html_body.text_content()
            return str(content)
        except AssertionError:
            # fx. for a empty document we get
            # AssertionError: ElementTree not initialized, missing root
            # Another way, instead of duck-typing, would be to check
            # xml = html.parse(fp)
            # if xml.getroot():
            #     return xml.xpath(...)
            # else: return None
            return None
