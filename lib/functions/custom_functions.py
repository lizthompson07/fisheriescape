def listrify(iterable):
    """
    Function takes in an iterable and returns a tidy list in string format. if the iterable is empty, a null string is returned
    """
    if len(iterable) == 0:
        return None
    else:
        return str([str(i) for i in iterable]).replace("[", "").replace("]", "").replace("'", "").replace('"', "")


def truncate(my_str, max_length):
    """
    This function takes a string an will return a string with a max length of var max_length
    """
    if len(my_str) > max_length:
        return "{}...".format(my_str[:max_length])
    else:
        return my_str
