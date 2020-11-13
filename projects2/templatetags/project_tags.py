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
def get_staff_field_list():
    try:
        return utils.get_staff_field_list()
    except Exception as e:
        print(e)
        return []


@register.simple_tag
def get_om_field_list():
    try:
        return utils.get_om_field_list()
    except Exception as e:
        print(e)
        return []

@register.simple_tag
def get_capital_field_list():
    try:
        return utils.get_capital_field_list()
    except Exception as e:
        print(e)
        return []
