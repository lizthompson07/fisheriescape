from django import template

register = template.Library()


@register.filter
def add(value, arg):
    return float(value)+float(arg)


@register.simple_tag
def add(value, arg):
    return float(value)+float(arg)
