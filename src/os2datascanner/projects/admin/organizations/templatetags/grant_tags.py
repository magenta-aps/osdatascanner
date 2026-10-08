# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django import template

from ..grant_utils import grant_create_url_map, grant_permission_map

register = template.Library()


@register.filter
def can_edit(perms, class_name: str):
    perm = f"change_{grant_permission_map(class_name)}"
    return perms["grants"][perm]


@register.filter
def can_add(perms, class_name: str):
    perm = f"add_{grant_permission_map(class_name)}"
    return perms["grants"][perm]


@register.filter
def grant_create_url_name(field_name: str):
    return grant_create_url_map(field_name)
