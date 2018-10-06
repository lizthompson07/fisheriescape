from django import template

register = template.Library()


@register.filter
def timedelta(value, arg):
    return (value-arg).days
