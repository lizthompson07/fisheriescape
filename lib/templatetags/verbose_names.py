from django import template
from django.template.defaultfilters import yesno
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field. DEPRECATED use get_verbose_label instead
    """
    return instance._meta.get_field(field_name).verbose_name.capitalize()


@register.simple_tag
def get_verbose_label(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    # check to see if there were any arguments passed in with the field name
    if len(field_name.split(".")) > 1:
        arg = field_name.split(".")[1]
        field_name = field_name.split(".")[0]

    # complicated little dance to make sure the first letter is capitalized.
    # Do not want to use the capitalize() method since it makes the remaining portion of str lowercase
    field_instance = instance._meta.get_field(field_name)
    verbose_name = field_instance.verbose_name
    first_letter = verbose_name[0].upper()
    str_list = list(verbose_name)
    str_list[0] = first_letter
    verbose_name = "".join(str_list)

    return verbose_name


@register.simple_tag
def get_field_value(instance, field_name, format=None, display_time=False, hyperlink=None):
    """
    Returns verbose_name for a field. To return a field from a foreign key, send in the field name as such: "user.first_name"
    """
    # check to see if there were any arguments passed in with the field name
    if len(field_name.split(".")) > 1:
        arg = field_name.split(".")[1]
        field_name = field_name.split(".")[0]
        try:
            field_value = getattr(getattr(instance, field_name), arg)
        except:
            field_value = ""

    else:
        field_instance = instance._meta.get_field(field_name)

        # first check if there is a value :
        if getattr(instance, field_name) is not None:
            # check to see if there are choices
            if len(field_instance.choices) > 0:
                field_value = getattr(instance, "get_{}_display".format(field_name))()

            # check to see if it is a datefield
            elif field_instance.get_internal_type() == 'DateTimeField':
                datetime_obj = getattr(instance, field_name)
                if display_time:
                    field_value = datetime_obj.strftime('%Y-%m-%d %H:%M')
                else:
                    field_value = datetime_obj.strftime('%Y-%m-%d')

            # check to see if it is a url
            elif str(getattr(instance, field_name)).startswith("http"):
                field_value = '<a href="{url}">{url}</a>'.format(url=getattr(instance, field_name))

            # check to see if it is a BooleanField
            elif field_instance.get_internal_type() == 'BooleanField' or field_instance.get_internal_type() == 'NullBooleanField':
                field_value = yesno(getattr(instance, field_name), "Yes,No,Unknown")

            # check to see if hyperlink was provided
            elif hyperlink:
                field_value = mark_safe('<a href="{}">{}</a>'.format(hyperlink, getattr(instance, field_name)))
            else:
                field_value = getattr(instance, field_name)
        else:
            field_value = "n/a"

    # TODO: specify special formatting
    if format == "currency":
        try:
            field_value = '${:,.2f}'.format(int(field_value))
        except:
            pass

    return field_value


@register.simple_tag
def verbose_field_display(instance, field_name, format=None, display_time=False, url=None):
    """
    Returns a standard display block for a field based on the verbose fieldname
    """
    field_instance = instance._meta.get_field(field_name)

    # call on the get_verbose_label func to handle label prep
    verbose_name = get_verbose_label(instance, field_name)

    # call on the get_field_value func to handle field value prep
    field_value = get_field_value(instance, field_name, format, display_time)

    if url and field_value != "n/a":
        html_block = '<p><span class="label">{}:</span><br><a href="{}">{}</a></p>'.format(verbose_name, url, field_value)
    else:
        html_block = '<p><span class="label">{}:</span><br>{}</p>'.format(verbose_name, field_value)

    return SafeString(html_block)
