from django.conf import settings

def my_envr(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {'MY_ENVR': settings.MY_ENVR}