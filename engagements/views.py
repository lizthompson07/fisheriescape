from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import DetailView
from django_tables2 import RequestConfig, LazyPaginator

from . import models, tables

def engagements_home(request):
    return render(request, 'engagements/engagements_home.html', {'nbar': 'home'})

def organization_list_view(request):
    table = tables.OrganizationListTable(models.Organization.objects.all())
    RequestConfig(request, paginate={
        'per_page': 10,
        'paginator_class': LazyPaginator
    }).configure(table)
    orgs = models.Organization.objects.all()
    return render(request, 'engagements/organization_list.html',
                  {
                      'table': table,
                      'org_table': orgs,
                      'nbar': 'organizations'
                  })

class OrganizationDetailView(DetailView):
    model = models.Organization
    template_name = 'engagements/organization_detail.html'
