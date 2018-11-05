from django import template
register = template.Library()

@register.simple_tag
def verbose_field_display(instance, field_name, format):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name.capitalize()
