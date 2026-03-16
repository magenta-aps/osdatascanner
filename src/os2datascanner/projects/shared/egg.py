# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

# https://www.folklore.org/Signing_Party.html

import hashlib

from django.conf import settings
from django.urls import register_converter
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class EggConverter:
    regex = r".+"
    targets = [
        "3fec17e8111c",  # en
        "c82e499f0e34",  # da
    ]

    def __init__(self):
        if settings.DEBUG:
            # Only in the development environment is "/developer/credits/"
            # valid
            self.targets = self.targets + [
                hashlib.sha384(b"developer/credits/").hexdigest()[-12:]
            ]

    def to_python(self, value):
        last_twelve = hashlib.sha384(value.encode()).hexdigest()[-12:]
        if last_twelve in self.targets:
            return value
        else:
            raise ValueError

    def to_url(self, value):
        raise ValueError


register_converter(EggConverter, "egg")


class EggView(LoginRequiredMixin, TemplateView):
    template_name = "components/credits/credits.html"
