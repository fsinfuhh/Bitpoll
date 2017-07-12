from django import template
from ..models import Poll, BitpollUser, PollWatch

register = template.Library()


@register.filter(name="is_watching")
def is_watching(user: BitpollUser, poll: Poll):
    return PollWatch.objects.filter(user=user, poll=poll).count() > 0
