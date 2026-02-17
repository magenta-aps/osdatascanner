# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django import template
from django.conf import settings

register = template.Library()


# Allows to get access to a settings value in a template.
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")
