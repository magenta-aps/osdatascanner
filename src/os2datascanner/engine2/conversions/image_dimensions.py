from PIL import Image

from .types import OutputType
from .registry import conversion


@conversion(OutputType.ImageDimensions,
            "image/png", "image/jpeg", "image/gif", "image/x-ms-bmp",
            # Many more MIME types have appeared for .bmp files. Groan
            "image/bmp", "image/x-bmp")
def dimensions_processor(r, **kwargs):
    try:
        with r.make_stream() as fp, Image.open(fp) as im:
            return im.width, im.height
    except OSError:
        return None
