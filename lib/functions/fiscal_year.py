from django.utils import timezone


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
