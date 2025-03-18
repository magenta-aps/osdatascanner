"""Convenience imports for using OS2datascanner interactively. (Note that the
shell_plus management command of the two Django projects has been configured to
import everything from this file by default.)"""
# flake8: noqa

from os2datascanner.engine2._interactive import *
from os2datascanner.utils.system_utilities import time_now
import os2datascanner.engine2.rules.logical_operators
import functools


from django.test import RequestFactory
request_factory = RequestFactory()


def _make_http_method(factory):

    def _method_impl(*args, **kwargs):
        request = factory(*args)
        for k, v in kwargs.items():
            setattr(request, k, v)
        return request
    return _method_impl


GET = _make_http_method(request_factory.get)
POST = _make_http_method(request_factory.post)
