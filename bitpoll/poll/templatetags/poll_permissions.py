from django import template

register = template.Library()


@register.filter
def poll_can_edit(poll, user) -> bool:
    return poll.can_edit(user)
