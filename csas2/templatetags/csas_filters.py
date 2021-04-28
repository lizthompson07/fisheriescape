from django import template

register = template.Library()


@register.filter
def is_markdown_field(value):
    target_field_list = [
        # request
        'issue',
        'rationale',
        'risk_text',
        # process
        'context',
        'objectives',
        'expected_publications',
    ]
    return value in target_field_list

