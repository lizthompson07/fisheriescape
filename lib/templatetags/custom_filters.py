from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """will multiple value and arg and return the product"""
    try:
        return float(value) * float(arg)
    except ValueError or TypeError:
        # if an error is encountered, just return 'value'
        return value


@register.filter
def nz(value, arg):
    """if a value is equal to None, this function will return arg instead"""
    if value is None:
        return arg
    else:
        return value


@register.filter
def zero2val(value, arg):
    """if a value is equal to zero, this function will return arg instead"""
    # weed out any possibility of errors
    try:
        float(value) == 0
    # if not able to cast, then just return 'value'
    except ValueError or TypeError:
        print("val={},arg={}".format(value, arg))
        return value
    else:
        #
        if float(value) == 0:
            return arg
        else:
            return value


@register.filter
def divide(value, arg):
    return float(nz(value,0)) / float(arg)


@register.filter
def percentage(value, arg=2):
    return format(value, ".{}%".format(arg))


@register.filter
def add(value, arg):
    return float(value)+float(arg)


@register.filter
def subtract(value, arg):
    return float(value)-float(arg)


@register.filter
def timedelta(value, arg):
    """the difference of two datetime objects in days"""
    return (value - arg).days


@register.filter
def tostring(value):
    """casts 'value' into a str """
    return str(value)
