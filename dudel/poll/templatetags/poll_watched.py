from django import template
from ..models import Poll, DudelUser, PollWatch

register = template.Library()


@register.filter(name="is_watching")
def is_watching(user: DudelUser, poll: Poll):
    return PollWatch.objects.filter(user=user, poll=poll).count() > 0
