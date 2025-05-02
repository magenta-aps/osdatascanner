from django import template

from ...adminapp.views.utils.grant_mixin import grant_permission_map

register = template.Library()


@register.filter
def can_edit(perms, class_name: str):
    perm = f"change_{grant_permission_map(class_name)}"
    return perms["grants"][perm]


@register.filter
def can_add(perms, class_name: str):
    perm = f"add_{grant_permission_map(class_name)}"
    return perms["grants"][perm]
