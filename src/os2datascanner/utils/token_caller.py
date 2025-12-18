from typing import Callable
from urllib.parse import urljoin
import requests
import functools

from os2datascanner.engine2.utilities.backoff import WebRetrier


def raw_request_decorator(fn):
    @functools.wraps(fn)
    def _wrapper(self, *args, check=True, **kwargs):
        response = fn(self, *args, **kwargs)
        if response.status_code == 401:
            # Mint a new token and try again
            self._token = self._token_creator()
            response = fn(self, *args, **kwargs)
        if check:
            response.raise_for_status()
        return response

    return _wrapper


class TokenCaller:
    """A TokenCaller is a simple wrapper around a requests.Session object that
    defines a base URL relative to which requests should be made and that
    automatically requests new bearer tokens from the server when necessary.
    That is. it's a helper class for web APIs that issue time-limited access
    tokens."""
    _common_session: requests.Session = requests.session()

    @classmethod
    def null_token_creator(cls):
        return None

    def __init__(
            self,
            token_creator: Callable[[], str],
            base_url: str,
            session=None):
        self._token_creator = token_creator
        self._token = token_creator()
        self._base_url = base_url

        self._session = session or self._common_session

        self.extra_kwargs = dict()

    def join(self, tail: str):
        if not tail:
            return self._base_url
        else:
            return urljoin(
                    self._base_url
                    + ("/" if not self._base_url.endswith("/") else ""),
                    tail.lstrip("/"))

    def _make_headers(self, base: dict[str, str]):
        return (base or {}) | ({
            "authorization": "Bearer {0}".format(self._token),
        } if self._token else {})

    @raw_request_decorator
    def _request(self, method, tail: str, **kwargs) -> requests.Response:
        kwargs["headers"] = self._make_headers(kwargs.get("headers"))
        return WebRetrier().run(
                method, self.join(tail),
                **(self.extra_kwargs | kwargs))

    def get(self, tail: str, **kwargs) -> requests.Response:
        return self._request(self._session.get, tail, **kwargs)

    def head(self, tail: str, **kwargs) -> requests.Response:
        return self._request(self._session.head, tail, **kwargs)

    def post(self, tail: str, **kwargs) -> requests.Response:
        return self._request(self._session.post, tail, **kwargs)

    def delete(self, tail: str, **kwargs) -> requests.Response:
        return self._request(self._session.delete, tail, **kwargs)

    def put(self, tail: str, **kwargs) -> requests.Response:
        return self._request(self._session.put, tail, **kwargs)

    def patch(self, tail: str, **kwargs) -> requests.Response:
        return self._request(self._session.patch, tail, **kwargs)
