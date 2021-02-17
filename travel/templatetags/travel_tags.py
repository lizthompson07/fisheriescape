from django import template

from travel import utils

register = template.Library()


@register.simple_tag
def get_request_field_list(tr=None, user=None):
    try:
        return utils.get_request_field_list(tr, user)
    except Exception as e:
        return []


@register.simple_tag
def get_traveller_field_list():
    try:
        return utils.get_traveller_field_list()
    except Exception as e:
        return []

@register.simple_tag
def get_request_reviewer_field_list():
    try:
        return utils.get_request_reviewer_field_list()
    except Exception as e:
        return []
