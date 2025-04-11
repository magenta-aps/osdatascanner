import os
from tempfile import NamedTemporaryFile
from subprocess import PIPE, DEVNULL


from os2datascanner.utils.system_utilities import run_custom
from ... import settings as engine2_settings
from ..types import OutputType
from ..registry import conversion, convert


def tesseract(path, dest="stdout", *args):
    result = run_custom(
            [
                "tesseract",
                *engine2_settings.tesseract["extra_args"],
                *args,
                path, dest
            ],
            universal_newlines=True,
            stdout=PIPE,
            stderr=DEVNULL,
            timeout=engine2_settings.subprocess["timeout"],
            isolate_tmp=True,
            # Disables multithreading for tesseract, which may lead to better performance.
            env=os.environ | {"OMP_THREAD_LIMIT": "1"})
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return None


def downscale_image_processor(r):
    """ Converts and/or resizes image to a 1500x1500 .png before running tesseract."""
    with r.make_path() as p, NamedTemporaryFile("rb", suffix=".png") as ntf:
        result = run_custom(
                ["convert", p, "-resize", "1500x", "png:{0}".format(ntf.name)], isolate_tmp=True)
        if result.returncode == 0:
            return tesseract(ntf.name)
        else:
            return None


@conversion(OutputType.Text, "image/png", "image/jpeg")
def image_processor(r):
    w, h = convert(r, OutputType.ImageDimensions)
    if w > 2000 or h > 2000:
        # An image much larger than this, will likely time out tesseract.
        return downscale_image_processor(r)
    else:
        with r.make_path() as p:
            return tesseract(p)


# Some ostensibly-supported image formats are handled badly by tesseract, so
# turn them into PNGs with ImageMagick's convert(1) command to make them more
# palatable
@conversion(OutputType.Text, "image/gif", "image/x-ms-bmp")
def intermediate_image_processor(r):
    with r.make_path() as p, NamedTemporaryFile("rb", suffix=".png") as ntf:
        result = run_custom(
                ["convert", p, "png:{0}".format(ntf.name)], isolate_tmp=True)
        if result.returncode == 0:
            return tesseract(ntf.name)
        else:
            return None
