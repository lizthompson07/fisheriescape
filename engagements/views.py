from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

from . import models

def engagements_home(request):
    return render(request, 'engagements/engagements_home.html', {'nbar': 'home'})

def organization_list_view(request):
    table_results = models.Organization.objects.all()
    template = loader.get_template('engagements/organization_list.html')
    context = {
        'org_table': table_results
    }
    return HttpResponse(template.render(context, request))
