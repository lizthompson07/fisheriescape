from django import template
from django.core.exceptions import FieldDoesNotExist
from django.template.defaultfilters import yesno
from django.utils.safestring import SafeString, mark_safe
import markdown

from lib.templatetags.custom_filters import tohtml

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
    To return a label from a foreign key, send in the field name as such: "user.first_name".
    To return a label from a model property, send in the property name as such: myprop|"label of my prop"
    """

    def __special_capitalize__(raw_string):
        """ Little dance to make sure the first letter is capitalized.
        Do not want to use the capitalize() method since it makes the remaining portion of str lowercase """
        first_letter = raw_string[0].upper()
        str_list = list(raw_string)
        str_list[0] = first_letter
        raw_string = "".join(str_list)
        return raw_string

    # 2019/04/03 - P. Upson
    # Added a test to see if the instance is 'null'. I was getting an issue on the diets/cruises page
    # during the get_verbose_label method due to the instance being passed in here being "None"
    # if the instance is null this method will return null.
    if instance is None:
        return None

    # check to see if there were any arguments passed in with the field name
    # this means the field is a foreign key so we will need to separate the first part preceding the "."
    if len(field_name.split(".")) > 1:
        field_name = field_name.split(".")[0]
        field_instance = instance._meta.get_field(field_name)
        verbose_name = field_instance.verbose_name
    # this means a model property was sent in
    elif len(field_name.split("|")) > 1:
        verbose_name = field_name.split("|")[1]
    # this means a plain old field_name was sent in
    else:
        field_instance = instance._meta.get_field(field_name)
        try:
            verbose_name = field_instance.verbose_name
        except AttributeError:
            # if there is no verbose_name attribute, just send back the field name
            verbose_name = field_name
    return mark_safe(__special_capitalize__(verbose_name))


@register.simple_tag
def get_field_value(instance, field_name, format=None, display_time=False, hyperlink=None, nullmark="---", date_format="%Y-%m-%d", safe=False):
    """
    Returns verbose_name for a field.
    To return a field from a foreign key, send in the field name as such: "user.first_name".
    To return a model property value, send in the property name as such: myprop|"label of my prop"
    """
    # check to see if there were any arguments passed in with the field name
    field_value = nullmark

    try:
        if len(field_name.split(".")) > 1:
            arg = field_name.split(".")[1]
            field_name = field_name.split(".")[0]
            field_value = getattr(getattr(instance, field_name), arg)

        elif len(field_name.split("|")) > 1:
            myprop = field_name.split("|")[0]
            field_value = getattr(instance, myprop)

        else:
            field_instance = instance._meta.get_field(field_name)

            # first check if there is a value :
            if getattr(instance, field_name) is not None and getattr(instance, field_name) != "":
                # check to see if it is a many to many field
                if field_instance.get_internal_type() == 'ManyToManyField' or field_instance.get_internal_type() == 'ManyToManyRel':
                    m2m = getattr(instance, field_name)
                    field_value = str([str(field) for field in m2m.all()]).replace("[", "").replace("]", "").replace("'",
                                                                                                                     "").replace(
                        '"', "")

                # check to see if there are choices
                elif len(field_instance.choices) > 0:
                    field_value = getattr(instance, "get_{}_display".format(field_name))()

                # check to see if it is a datefield
                elif field_instance.get_internal_type() == 'DateTimeField':
                    if not date_format:
                        date_format = "%Y-%m-%d"
                    datetime_obj = getattr(instance, field_name)
                    if display_time:
                        field_value = datetime_obj.strftime('{} %H:%M'.format(date_format))
                    else:
                        field_value = datetime_obj.strftime(date_format)

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
                field_value = nullmark
    except:
        print("Could not evaluate field value for '" + str(field_name) + "' for object '" + str(type(instance)) + "'")
        field_value = nullmark

    # TODO: specify special formatting
    if format == "currency":
        try:
            field_value = '${:,.2f}'.format(float(field_value))
        except:
            pass

    field_value = markdown.markdown(field_value) if "HTML" in str(format) else field_value
    field_value = mark_safe(field_value) if safe else field_value
    return field_value



@register.simple_tag
def verbose_field_display(instance, field_name, format=None, display_time=False, url=None, date_format=None):
    """
    Returns a standard display block for a field based on the verbose fieldname
    """

    # call on the get_verbose_label func to handle label prep
    verbose_name = get_verbose_label(instance, field_name)

    # call on the get_field_value func to handle field value prep
    field_value = get_field_value(instance, field_name, format=format, display_time=display_time, date_format=date_format)

    if url and field_value != "n/a":
        html_block = '<p><span class="label">{}:</span><br><a href="{}">{}</a></p>'.format(verbose_name, url, field_value)
    else:
        html_block = '<p><span class="label">{}:</span><br>{}</p>'.format(verbose_name, field_value)

    return SafeString(html_block)


@register.simple_tag
def verbose_td_display(instance, field_name, format=None, display_time=False, url=None, date_format=None, nullmark="---", th_width=None,
                       td_width=None, to_html=False):
    """
    returns a table row <tr> with a <td> for the label and a <td> for the value. Call this from within a <table>
    """
    # call on the get_verbose_label func to handle label prep
    verbose_name = get_verbose_label(instance, field_name)

    # call on the get_field_value func to handle field value prep
    field_value = get_field_value(instance, field_name, format=format, display_time=display_time, date_format=date_format,
                                  nullmark=nullmark)

    if to_html:
        field_value = tohtml(field_value)

    th_tag_opener = '<th style="width: {};">'.format(th_width) if th_width else '<th>'
    td_tag_opener = '<td style="width: {};">'.format(td_width) if td_width else '<td>'

    if url and field_value != "n/a":
        html_block = '<tr>{}{}</th>{}<a href="{}">{}</a></td></tr>'.format(th_tag_opener, verbose_name, td_tag_opener, url, field_value)
    else:
        html_block = '<tr>{}{}</th>{}{}</td></tr>'.format(th_tag_opener, verbose_name, td_tag_opener, field_value)


    return SafeString(html_block)
