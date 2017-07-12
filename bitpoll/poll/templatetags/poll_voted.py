from django import template
from ..models import Poll, Vote, BitpollUser

register = template.Library()


@register.filter(name='has_voted')
def has_voted(user: BitpollUser, poll: Poll):
    return Vote.objects.filter(user=user, poll=poll).count() > 0
