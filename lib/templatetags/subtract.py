from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    return float(value)-float(arg)

@register.simple_tag
def subtract(value, arg):
    return float(value)-float(arg)
