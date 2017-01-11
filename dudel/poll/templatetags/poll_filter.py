from django import template

from dudel.poll.util import PartialDateTime

register = template.Library()


@register.filter
def group_title(value):
    if isinstance(value, PartialDateTime):
        return value.format()
    else:
        return value


@register.filter
def percentage(value: int) -> str:
    return '{0:.1f}%'.format(value * 100)
