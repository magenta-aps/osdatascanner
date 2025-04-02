from typing import Callable
from urllib.parse import urljoin
import requests
import functools

from os2datascanner.engine2.utilities.backoff import WebRetrier


def raw_request_decorator(fn):
    @functools.wraps(fn)
    def _wrapper(self, *args, _retry=False, **kwargs):
        response = fn(self, *args, **kwargs)
        try:
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as ex:
            # If _retry, it means we have a status code 401 but are trying a second time.
            # It should've succeeded the first time, so we raise an exc to avoid a potential
            # endless loop
            if ex.response.status_code != 401 or _retry:
                raise ex
            self._token = self._token_creator()
            return _wrapper(self, *args, _retry=True, **kwargs)

    return _wrapper


class TokenCaller:
    """A TokenCaller is a simple wrapper around a requests.Session object that
    defines a base URL relative to which requests should be made and that
    automatically requests new bearer tokens from the server when necessary.
    That is. it's a helper class for web APIs that issue time-limited access
    tokens."""
    _common_session: requests.Session = requests.session()

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

    def _make_headers(self, base: dict[str, str]):
        return (base or {}) | {
            "authorization": "Bearer {0}".format(self._token),
        }

    @raw_request_decorator
    def _request(self, method, tail: str, **kwargs) -> requests.Response:
        kwargs["headers"] = self._make_headers(kwargs.get("headers"))
        return WebRetrier().run(
                method, urljoin(self._base_url + "/", tail.lstrip("/")),
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
