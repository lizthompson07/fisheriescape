from django import template

register = template.Library()


@register.filter
def nz(value, arg):
    if value == None:
        return arg
    else:
        return value
