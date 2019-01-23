from django import template
from django.utils.safestring import SafeString

def verbose_field_name(instance, field_name):
    """
    Returns a standard display block for a field based on the verbose fieldname
    """
    try:
        field_instance = instance._meta.get_field(field_name)
    except AttributeError:
        verbose_name = field_name
    else:
        verbose_name = field_instance.verbose_name

        # complicated little dance to make sure the first letter is capitalized.
        # Do not want to use the capitalize() method since it makes the remaining portion of str lowercase
        first_letter = verbose_name[0].upper()
        str_list = list(verbose_name)
        str_list[0] = first_letter
        verbose_name = "".join(str_list)

    return verbose_name

