from django import template

register = template.Library()

@register.filter
def percentage(value,arg=2):
    return format(value, ".{}%".format(arg))
