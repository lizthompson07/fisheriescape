from whalesdb import models


def whales_authorized(user):
    return user.is_authenticated and user.groups.filter(name='whalesdb_admin').exists()


def get_help_text_dict(model=None):
    print("Model: '{}'".format(str(model.__name__)))
    my_dict = {}
    if not model:
        for obj in models.HelpText.objects.all():
            my_dict[obj.field_name] = str(obj)
    else:
        # If a model is supplied get the fields specific to that model
        for obj in models.HelpText.objects.filter(model=str(model.__name__)):
            my_dict[obj.field_name] = str(obj)

    return my_dict
