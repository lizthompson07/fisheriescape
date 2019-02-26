import math
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.db.models import TextField
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from easy_pdf.views import PDFTemplateView

from lib.functions.nz import nz
from . import models
from . import forms
from . import filters


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'masterlist/close_me.html'


def in_masterlist_group(user):
    if user:
        return user.groups.filter(name='masterlist_access').count() != 0


class MasterListAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_masterlist_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_masterlist_admin_group(user):
    if user:
        return user.groups.filter(name='masterlist_admin').count() != 0


class MasterListAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_masterlist_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(MasterListAccessRequiredMixin, TemplateView):
    template_name = 'masterlist/index.html'


# PERSON #
##########

class PersonListView(MasterListAccessRequiredMixin, FilterView):
    template_name = 'masterlist/person_list.html'
    filterset_class = filters.PersonFilter
    model = models.Person
    queryset = models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'notes', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Person.objects.first()
        context["field_list"] = [
            'last_name',
            'first_name',
            'phone_1',
            'phone_2',
            'email',
        ]
        return context


class PersonDetailView(MasterListAccessRequiredMixin, DetailView):
    model = models.Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'first_name',
            'last_name',
            'phone_1',
            'phone_2',
            'fax',
            'email',
            'notes',
        ]
        return context


class PersonUpdateView(MasterListAccessRequiredMixin, UpdateView):
    model = models.Person
    form_class = forms.PersonForm


class PersonUpdateViewPopout(MasterListAccessRequiredMixin, UpdateView):
    template_name = 'masterlist/person_form_popout.html'
    model = models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('masterlist:close_me'))


class PersonCreateView(MasterListAccessRequiredMixin, CreateView):
    model = models.Organization
    form_class = forms.PersonForm

    def get_initial(self):
            return {'last_modified_by': self.request.user}

class PersonCreateViewPopout(MasterListAccessRequiredMixin, CreateView):
    template_name = 'masterlist/person_form_popout.html'
    model = models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('masterlist:close_me'))

    def get_initial(self):
            return {'last_modified_by': self.request.user}

class PersonDeleteView(MasterListAdminRequiredMixin, DeleteView):
    model = models.Person
    success_url = reverse_lazy('masterlist:person_list')
    success_message = 'The person was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# ORGANIZATION #
################

class OrganizationListView(MasterListAccessRequiredMixin, FilterView):
    template_name = 'masterlist/organization_list.html'
    filterset_class = filters.OrganizationFilter
    model = models.Organization
    queryset = models.Organization.objects.annotate(
        search_term=Concat('name_eng', 'name_fre', 'abbrev', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Organization.objects.first()
        context["field_list"] = [
            'name_eng',
            'name_fre',
            'name_ind',
            'province',
        ]
        return context


class OrganizationDetailView(MasterListAccessRequiredMixin, DetailView):
    model = models.Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name_eng',
            'name_fre',
            'name_ind',
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
            'key_species',
            'dfo_contact_instructions',
            'notes',
            'grouping',
            'regions',
            'sectors',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class OrganizationUpdateView(MasterListAccessRequiredMixin, UpdateView):
    model = models.Organization
    form_class = forms.OrganizationForm

    def get_initial(self):
            return {'last_modified_by': self.request.user}

class OrganizationCreateView(MasterListAccessRequiredMixin, CreateView):
    model = models.Organization
    form_class = forms.OrganizationForm

    def get_initial(self):
            return {'last_modified_by': self.request.user}


class OrganizationDeleteView(MasterListAdminRequiredMixin, DeleteView):
    model = models.Organization
    success_url = reverse_lazy('masterlist:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# MEMBER  (ORGANIZATION PERSON) #
#################################

class MemberCreateView(MasterListAccessRequiredMixin, CreateView):
    model = models.OrganizationMember
    template_name = 'masterlist/member_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.MemberForm

    def get_initial(self):
        org = models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = models.Organization.objects.get(id=self.kwargs['org'])
        context['organization'] = org

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('masterlist:close_me'))


class MemberUpdateView(MasterListAccessRequiredMixin, UpdateView):
    model = models.OrganizationMember
    template_name = 'masterlist/member_form_popout.html'
    form_class = forms.MemberForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('masterlist:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }

def member_delete(request, pk):
    object = models.OrganizationMember.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The member has been successfully deleted from the organization."))
    return HttpResponseRedirect(reverse_lazy("masterlist:org_detail", kwargs={"pk": object.organization.id}))

