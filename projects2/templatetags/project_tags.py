from django import template

from lib.templatetags.custom_filters import nz
from projects2 import utils

register = template.Library()


@register.simple_tag
def get_project_year_field_list(project_year):
    try:
        return utils.get_project_year_field_list(project_year)
    except Exception as e:
        print(e)
        return []


@register.simple_tag
def add(value, arg):
    return float(nz(value, 0)) + float(nz(arg, 0))


@register.simple_tag
def subtract(value, arg):
    return float(nz(value, 0)) - float(nz(arg, 0))


@register.simple_tag
def echo(value):
    return value


@register.simple_tag
def crash_if_none(var_name, value):
    if nz(value, None) is None:
        raise Exception(f'the expected template variable: "{var_name}" is missing in the context')
    else:
        return ""
