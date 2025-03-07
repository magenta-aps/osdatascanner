from django import template

register = template.Library()


@register.filter
def can_edit(perms, class_name: str):
    perm = f"change_{class_name.lower().replace('_', '')}"
    return perms["grants"][perm]


@register.filter
def can_add(perms, class_name: str):
    perm = f"add_{class_name.lower().replace('_', '')}"
    return perms["grants"][perm]
