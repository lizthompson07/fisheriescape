from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

from . import models

def engagements_home(request):
    return render(request, 'engagements/engagements_home.html', {'nbar': 'home'})

