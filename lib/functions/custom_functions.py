def listrify(iterable):
    """
    Function takes in an iterable and returns a tidy list in string format. if the iterable is empty, a null string is returned
    """
    if len(iterable) == 0:
        return None
    else:
        return str([str(i) for i in iterable]).replace("[", "").replace("]", "").replace("'", "").replace('"', "")



