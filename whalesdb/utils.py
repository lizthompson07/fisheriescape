from whalesdb import models


def whales_authorized(user):
    return user.is_authenticated and user.groups.filter(name='whalesdb_admin').exists()


def get_help_text_dict():
    my_dict = {}
    for obj in models.HelpText.objects.all():
        my_dict[obj.field_name] = str(obj)

    return my_dict
