import datetime

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.text import slugify
from django.urls import reverse_lazy
from django_tables2 import RequestConfig, LazyPaginator, SingleTableView

from .models import Organization
from .tables import OrganizationListTable
from .forms import OrganizationCreateForm, OrganizationForm


def engagements_home(request):
    return render(request, 'engagements/engagements_home.html', {'nbar': 'home'})


class OrganizationListView(SingleTableView):
    model = Organization
    template_name = 'engagements/organization_list.html'
    table_class = OrganizationListTable
    paginate_by = 10
    context_object_name = 'table'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nbar'] = 'organizations'
        return context


class OrganizationDetailView(DetailView):
    model = Organization
    template_name = 'engagements/organization_detail.html'


class OrganizationCreateView(CreateView):
    # form_class to specify a Form class in forms.py for extra validation and widget styling/selection
    model = Organization
    form_class = OrganizationCreateForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = form.instance.created_by
        form.instance.slug = slugify(form.instance.__str__())

        return super().form_valid(form)


class OrganizationUpdateView(UpdateView):
    model = Organization
    form_class = OrganizationForm

    def form_valid(self, form):
        form.instance.last_modified_by = self.request.user

        return super().form_valid(form)


class OrganizationDeleteView(DeleteView):
    model = Organization
    success_url = reverse_lazy('engagements:organization_list')
