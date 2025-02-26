import gettext
from importlib import resources

from os2datascanner.engine2 import settings


LOCALE_PATH = resources.files("os2datascanner.engine2").joinpath("locale")

t = langs = None
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

gettext = t.gettext
del t, langs, LOCALE_PATH
__all__ = ["gettext"]
