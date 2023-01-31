from django import template

register = template.Library()

@register.filter
def has_role(resource, user):
    return resource.resource_people2.filter(user=user).exists()


@register.filter
def strip_label(val):
    try:
        return val.split("|")[0]
    except:
        return val