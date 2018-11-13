from django import template
from django.utils.safestring import SafeString
register = template.Library()

@register.simple_tag
def verbose_field_display(instance, field_name, format=None):
    """
    Returns a standard display block for a field based on the verbose fieldname
    """

    field_instance = instance._meta.get_field(field_name)
    verbose_name = field_instance.verbose_name

    # complicated little dance to make sure the first letter is capitalized.
    # Do not want to use the capitalize() method since it makes the remaining portion of str lowercase
    first_letter = verbose_name[0].upper()
    str_list = list(verbose_name)
    str_list[0] = first_letter
    verbose_name = "".join(str_list)

    # first check if there is a value :
    if getattr(instance, field_name):

        # check to see if there are choices
        if len(field_instance.choices) > 0 :
            field_value = getattr(instance, "get_{}_display".format(field_name))()


        # check to see if it is a datefield
        elif field_instance.get_internal_type() == 'DateTimeField':
            datetime_obj = getattr(instance, field_name)
            field_value = datetime_obj.strftime('%Y-%m-%d')

        # check to see if it is a url
        elif str(getattr(instance, field_name)).startswith("http"):
            field_value = '<a href="{url}">{url}</a>'.format(url=getattr(instance, field_name))

        else:
            field_value = getattr(instance, field_name)
    else:
        field_value = getattr(instance, field_name)

    # TODO: create other formats for displaying block
    if format:
        html_block = ""

    # go to the default format
    else:
        html_block = '<p><span class="label">{}:</span><br>{}</p>'.format(verbose_name, field_value)

    return SafeString(html_block)


