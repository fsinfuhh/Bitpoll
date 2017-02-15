from numbers import Number

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
def percentage(value: Number) -> str:
    if value is not None:
        return '{0:.1f}%'.format(value * 100)
    return 'n/a'


@register.filter
def or_none(value: object) -> object:
    if value:
        return value
    return 'n/a'
