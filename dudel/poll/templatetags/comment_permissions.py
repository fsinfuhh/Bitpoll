from django import template

register = template.Library()


@register.filter
def comment_can_edit(comment, user) -> bool:
    return comment.can_edit(user)
