from django import template
from django.utils.safestring import SafeString
from lib.templatetags.custom_filters import tohtml
from lib.templatetags.verbose_names import get_verbose_label, get_field_value

register = template.Library()

@register.simple_tag
def details_display(instance, field_name, nullmark="---"):
    verbose_name = get_verbose_label(instance, field_name)
    field_value = get_field_value(instance, field_name, nullmark=nullmark)

    th_tag_opener = f'<th id="{field_name}">'
    td_tag_opener = '<td>'

    html_block = "<tr>{}{}</th>{}{}</td></tr>".format(th_tag_opener, verbose_name, td_tag_opener, field_value)
    return SafeString(html_block)

@register.simple_tag
def details_li_display(instance, field_name, nullmark="---"):
    field_value = get_field_value(instance, field_name, nullmark=nullmark)

    li_tag_opener = "<li>"
    items = field_value.split(";")
    items = [item.strip() for item in items]

    html_block = ""
    if field_value != "":
        for item in items:
            html_block += "{}{}</li>".format(li_tag_opener, item)

    return SafeString(html_block)
    
@register.simple_tag
def details_table_of_contents_display(instance, field_name, nullmark="---"):
    verbose_name = get_verbose_label(instance, field_name)
    html_block = "<a class=\"details_table_of_contents\" onclick=\"jump('{}')\">{}</a><br>".format(field_name, verbose_name)
    return SafeString(html_block)