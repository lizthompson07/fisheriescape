from whalesdb import models
from django.http import JsonResponse
import re

def whales_authorized(user):
    return user.is_authenticated and user.groups.filter(name='whalesdb_admin').exists()


def get_help_text_dict(model=None, title=''):
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


def ajax_get_fields(request):
    model_name = request.GET.get('model', None)

    # use the model name passed from the web page to find the model in the apps models file
    model = models.__dict__[model_name]

    # use the retrieved model and get the doc string which is a string in the format
    # SomeModelName(id, field1, field2, field3)
    # remove the trailing parentheses, split the string up based on ', ', then drop the first element
    # which is the model name and the id.
    match = str(model.__dict__['__doc__']).replace(")", "").split(", ")[1:]

    data = {
        'fields': match
    }

    return JsonResponse(data)