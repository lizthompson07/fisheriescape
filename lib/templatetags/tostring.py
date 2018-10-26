from django import template

register = template.Library()


@register.filter
def tostring(value):
    return str(value)
