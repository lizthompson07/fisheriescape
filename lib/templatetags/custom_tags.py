from django import template
from django.template.defaultfilters import yesno
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.simple_tag
def get_subset(iterable, index):
    """
    Returns a subset of an iterable
    """
    try:
        value = iterable[int(index)]
    except IndexError or TypeError:
        if TypeError:
            print("index provided is of an invalid type")
        if IndexError:
            print("value does not exist at the index provided")
        value = None

    return value


@register.filter(name='lookup')
def lookup(my_dict, key):
    """lookup the value of a dictionary. value is a dictionary object and arg is the key"""
    return my_dict[key]


@register.simple_tag
def add(value, arg):
    return float(value) + float(arg)


@register.simple_tag
def subtract(value, arg):
    return float(value) - float(arg)
