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

            # Excluding metadata content:
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Content_categories#metadata_content
            for blob in html_body.xpath('//base | //link | //meta | //noscript |'
                                        '//script | //style | //template | //title'):
                blob.getparent().remove(blob)

            for br in html_body.xpath("//br | //p | //div"):
                # lxml represents loose text strings after inline elements by
                # attaching them to the preceding element as a "tail":
                #
                # >>> (doc := html.fromstring("<p>one<br>two<br>three</p>"))
                # <Element p at 0x7ff21c5aea20>
                # >>> doc.text
                # 'one'
                # >>> (fc := doc.getchildren()[0])
                # <Element br at 0x7ff21c5aeca0>
                # >>> fc.tail
                # 'two'
                #
                # We can add things to the tail ourselves to make the
                # document's plain text representation nicer:
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
