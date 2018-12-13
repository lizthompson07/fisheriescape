def nz(value, arg=None):
    """
    Function will look at "value" and if is it is 0, None or "" it will return arg; otherwise will just return value
    """
    print(value)
    if value is None or value == "" or value == 0 or value == "None":
        return arg
    else:
        return value


