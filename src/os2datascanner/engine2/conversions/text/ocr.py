# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import structlog
from subprocess import PIPE, DEVNULL, CalledProcessError, TimeoutExpired
from tempfile import TemporaryDirectory
from ... import settings as engine2_settings
from ....utils.system_utilities import run_custom
from ..abort import current_abort_check
from ..types import OutputType
from ..registry import conversion

logger = structlog.get_logger("engine2")

# Absolute path to the OCR CLI worker. Invoked by filesystem path (not
# `python -m ...`) so the subprocess doesn't have to run engine2's package-init every time.
_OCR_CLI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "utilities", "_ocr_cli.py")


def tesseract_pymupdf(image_bytes, filetype=None):
    """Performs OCR on in-memory image bytes via a subprocess pymupdf
    worker.

    The actual Tesseract/MuPDF work happens in a subprocess so that f.e. a
    segfault in either library cannot kill the engine2 worker.

    Timeout and process-group cleanup are enforced by run_custom().
    """
    should_abort = current_abort_check.get()
    if should_abort and should_abort():
        return None

    logger.info("Running tesseract with pymupdf (in a subprocess)")
    with TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, "in.bin")
        out_path = os.path.join(tmpdir, "out.txt")
        with open(in_path, "wb") as f:
            f.write(image_bytes)

        try:
            run_custom(
                    # in_path and out_path are arguments to the OCR cli.
                    [sys.executable, _OCR_CLI, in_path, out_path],
                    stdout=DEVNULL, stderr=DEVNULL,
                    timeout=engine2_settings.subprocess["timeout"],
                    kill_group=True, isolate_tmp=True, check=True,
                    env=os.environ | {"OMP_THREAD_LIMIT": "1"})
        except (CalledProcessError, TimeoutExpired) as e:
            # TODO: I'm not sure if this is always right, but it's what our testsuite expects.
            # See test_corrupted_ocr in test_images.py.

            # Corrupted image, segfault inside pymupdf/Tesseract, or a hang:
            # treat as "this image isn't OCRable" rather than failing the whole
            # conversion.
            logger.warning(
                    "OCR subprocess failed", filetype=filetype, exc_info=e)
            return None

        with open(out_path, "rb") as f:
            # errors=replace inserts "U+FFFD" on invalid bytes instead of crashing.
            # I guess that's more reasonable than crashing in OCR context.
            text = f.read().decode("utf-8", errors="replace").strip()

    return text or None


def tesseract_cli(path, dest="stdout", *args):
    """
    Wrapper for the tesseract command-line tool for specialized conversions.
    (Currently used for MRZ only)
    """
    logger.info("Running tesseract command-line tool")
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


@conversion(OutputType.Text,
            "image/png", "image/jpeg", "image/gif", "image/x-ms-bmp",
            "image/bmp", "image/x-bmp")
def image_processor(r):
    """
    Uses pymupdf's tesseract bindings to extract text from common image types using in-memory OCR.
    Downscales large images to prevent timeouts and improve performance.
    """
    should_abort = current_abort_check.get()
    if should_abort and should_abort():
        return None
    with r.make_stream() as stream:
        image_bytes = stream.read()
    # Get the file extension from the resource's handle name
    file_ext = r.handle.name.split('.')[-1].lower()
    return tesseract_pymupdf(image_bytes, filetype=file_ext)
