from . import settings
from .utilities.backoff import WebRetrier


def _make_kwargs(base_dict, *keys, **kwargs):
    rv = {}
    for key, ctr in keys:
        match (kwargs.get(key), base_dict.get(key)):
            case None, None:
                pass
            case kwv, _:
                rv[key] = ctr(kwv)
            case None, nodev:
                rv[key] = ctr(nodev)
    return rv


def make_webretrier(**kwargs) -> WebRetrier:
    """Returns a WebCrawler pre-configured with all of the settings defined in
    the model.http node. (These settings can be overwritten by the keyword
    arguments to this function.)"""
    kwargs = _make_kwargs(
            settings.model["http"],

            # CountingRetrier
            ("max_tries", int),
            ("warn_after", int),
            # ExponentialBackoffRetrier
            ("base", int),
            ("ceiling", int),
            ("fuzz", float),

            **kwargs)

    return WebRetrier(**kwargs)
