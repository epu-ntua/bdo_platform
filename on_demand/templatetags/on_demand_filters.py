from django import template

register = template.Library()


@register.filter
def has_upvoted(request, user):
    if not user.is_authenticated():
        return False

    return request.upvotes.filter(user=user).exists()
