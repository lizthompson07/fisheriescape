from django import template
from django.template.defaultfilters import yesno
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.simple_tag
def get_subset(iterable, index):
    """
    Returns a subset of an interable
    """
    try:
        value = iterable[index]
    except:
        value = None

    return value

