"""
Contains utilities for compressing PDF files using GhostScript.
"""
import shlex
import structlog

from tempfile import TemporaryDirectory

from .....utils.system_utilities import run_custom
from .... import settings as engine2_settings

GS = engine2_settings.ghostscript


logger = structlog.get_logger("engine2")


def gs_convert(path):
    '''Convert to a compressed form using GhostScript (gs).'''
    with TemporaryDirectory() as outputdir:
        match GS["_base_arguments"]:
            case list() as bl:
                base_arguments = bl
            case str() as bs:
                logger.warning(
                        "deprecated type for setting"
                        " 'ghostscript._base_arguments';"
                        " use a list instead")
                base_arguments = shlex.split(bs)
            case _:
                raise TypeError

        match GS["extra_args"]:
            case list() as el:
                extra_args = el
            case str() as es:
                logger.warning(
                        "deprecated type for setting"
                        " 'ghostscript.extra_args';"
                        " use a list instead")
                base_arguments = shlex.split(es)
            case _:
                raise TypeError

        converted_path = "{0}/gs-temporary.pdf".format(outputdir)
        command = ["gs", "-q",
                   *base_arguments,
                   f"-dPDFSETTINGS={GS['pdf_profile']}",
                   "-sOutputFile={0}".format(converted_path),
                   *extra_args,
                   path]

        run_custom(command,
                   timeout=GS["timeout"],
                   check=True, isolate_tmp=True)

        yield converted_path
