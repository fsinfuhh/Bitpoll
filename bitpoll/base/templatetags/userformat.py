from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def format_user(user, format='full'):
    if format == 'full':
        full_name = conditional_escape(user.get_full_name())
        username = conditional_escape(user.username)
        result = u'{0} <span class="user-username">({1})</span>'.format(
                full_name, username)
    elif format == 'name':
        result = conditional_escape(user.get_full_name())
    elif format == 'username':
        result = conditional_escape(user.username)
    elif format == 'email':
        return u'{0} ({1})'.format(user.get_full_name(), user.username)
    else:
        raise ValueError("Invalid format for format_user")

    return mark_safe(result)
