import yaml
from django import template


register = template.Library()


@register.filter
def as_dict(something):
    return dict(something)


@register.filter
def as_yaml(something):
    return yaml.dump(something).strip()
