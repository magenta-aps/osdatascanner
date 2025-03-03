import gettext
import warnings
from importlib import resources

from os2datascanner.engine2 import settings


LOCALE_PATH = resources.files("os2datascanner.engine2").joinpath("locale")

t = langs = None
try:
    match (settings.USE_I18N, settings.LANGUAGES):
        case (True, []):
            # I18N is enabled, but the list of languages is empty. Allow gettext to
            # do its default lookups
            t = gettext.translation("osds_engine2", LOCALE_PATH)
        case (True, [*langs]):
            # I18N is enabled and the list of languages is populated
            t = gettext.translation("osds_engine2", LOCALE_PATH, languages=langs)
        case (False, _):
            # I18N is disabled. Suppress language autodetection and return a
            # dummy translations object
            t = gettext.translation(
                    "osds_engine2", LOCALE_PATH, languages=[], fallback=True)
except FileNotFoundError:
    if not settings.DEBUG:
        raise

    # In debug mode, and in debug mode only, we let the user get away with this
    warnings.warn(
            f"couldn't find an osds_engine2.mo file in {LOCALE_PATH},"
            " running without engine2 translations")
    t = gettext.NullTranslations()

gettext = t.gettext
del t, langs, LOCALE_PATH
__all__ = ["gettext"]
