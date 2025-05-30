from os import getenv
from sys import stderr
import requests
import structlog

from os2datascanner.utils.debug import add_debug_function


logger = structlog.get_logger("utils")


def _default_wrapper(function, *args, **kwargs):
    return function(*args, **kwargs)


__ltr = None


def mint_cc_token_raw(
        endpoint: str,  # URL
        client_id: str,
        client_secret: str,
        *, wrapper=None, post_timeout=60, **kwargs) -> requests.Response:
    """Retrieves a token from the given endpoint following the OAuth 2.0
    client credentials flow.

    All keyword arguments are passed into the JSON body of the request, apart
    from two: the wrapper argument can be set to wrap this operation in (for
    example) a retrier, and the post_timeout argument can be set to specify a
    timeout for the HTTP POST request."""
    global __ltr

    response = (wrapper or _default_wrapper)(
            requests.post,
            endpoint,
            {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                **kwargs
            },
            timeout=post_timeout)
    __ltr = response

    response.raise_for_status()
    return response


def mint_cc_token(*args, **kwargs) -> str:
    """As mint_cc_token_raw, but automatically unpacks and returns the token
    from the JSON body of the response."""
    return mint_cc_token_raw(*args, **kwargs).json()["access_token"]


__all__ = [
    "mint_cc_token_raw", "mint_cc_token",
]


if getenv("OSDS_DEBUG_OAUTH2", None):
    @add_debug_function
    def print_last_cc_token(signum, frame):
        print("[OSDS_DEBUG_OAUTH2] Last token response:", file=stderr)
        print(f"  {__ltr.json() if __ltr else None}", file=stderr)
