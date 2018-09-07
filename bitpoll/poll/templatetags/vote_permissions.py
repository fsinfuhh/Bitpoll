from django import template

from bitpoll.poll.models import Vote

register = template.Library()


@register.filter
def vote_can_edit(vote: Vote, user) -> bool:
    return vote.can_edit(user)


@register.filter
def vote_can_delete(vote: Vote, user) -> bool:
    return vote.can_delete(user)
