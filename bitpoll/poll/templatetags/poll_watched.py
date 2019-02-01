from django import template
from ..models import Poll, BitpollUser, PollWatch

register = template.Library()


@register.filter(name="is_watching")
def is_watching(user: BitpollUser, poll: Poll):
    return poll.user_watches(user)


@register.filter(name="can_watch")
def can_watch(user: BitpollUser, poll: Poll):
    return poll.can_watch(user)
