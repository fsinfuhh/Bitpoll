from django import template
from django.contrib.auth.models import AbstractUser

from bitpoll.poll.models import Poll

register = template.Library()


@register.filter
def poll_can_edit(poll: Poll, user: AbstractUser) -> bool:
    return poll.can_edit(user)


@register.filter
def poll_is_owner(poll: Poll, user: AbstractUser) -> bool:
    return poll.is_owner(user)
