from django.utils import timezone

def nz(value, arg=None):
    """
    Function will look at "value" and if is it is 0, None or "" it will return arg; otherwise will just return value
    """
    if value is None or value == "" or value == 0:
        return arg
    else:
        return value


def fiscal_year(next=False, date=timezone.now(), sap_style=False):
    """
    Function will return a fiscal year value. if no arg is given, current date will be used.
    """

    if date.month >= 4:
        if next:
            if sap_style:
                return int("{}".format(date.year + 2))
            else:
                return "{}-{}".format(date.year + 1, date.year + 2)
        else:
            if sap_style:
                return int("{}".format(date.year + 1))
            else:
                return "{}-{}".format(date.year, date.year + 1)
    else:
        if next:
            if sap_style:
                return int("{}".format(date.year + 1))
            else:
                return "{}-{}".format(date.year, date.year + 1)
        else:
            if sap_style:
                return int("{}".format(date.year))
            else:
                return "{}-{}".format(date.year - 1, date.year)


def listrify(iterable, separator=", "):
    """
    Function takes in an iterable and returns a tidy list in string format. if the iterable is empty, a null string is returned
    """
    if len(iterable) == 0:
        return None
    else:
        return str([str(i) for i in iterable]).replace("[", "").replace("]", "").replace("'", "").replace('"', "").replace(", ", separator)


def truncate(my_str, max_length):
    """
    This function takes a string an will return a string with a max length of var max_length
    """
    if len(my_str) > max_length:
        return "{}...".format(my_str[:max_length])
    else:
        return my_str


def attr_error_2_none(obj, attr):
    """This function will look for an Attribute Error and if found will return None object. Otherwise it will return attr"""
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None
