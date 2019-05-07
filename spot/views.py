import os
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import TextField
from django.db.models.functions import Concat
from django.utils import timezone
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###

from lib.functions.nz import nz
from . import models
from . import forms
from . import filters
from . import reports
from masterlist import models as ml_models


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'spot/close_me.html'


def in_spot_group(user):
    if user:
        return user.groups.filter(name='spot_access').count() != 0


class SpotAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_spot_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


def in_spot_admin_group(user):
    if user:
        return user.groups.filter(name='spot_admin').count() != 0


class SpotAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_spot_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/')
        return super().dispatch(request, *args, **kwargs)


class IndexTemplateView(SpotAccessRequiredMixin, TemplateView):
    template_name = 'spot/index.html'


# ORGANIZATION #
################

class OrganizationListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/organization_list.html'
    filterset_class = filters.OrganizationFilter
    model = ml_models.Organization
    queryset = ml_models.Organization.objects.annotate(
        search_term=Concat('name_eng', 'name_fre', 'abbrev', 'id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = ml_models.Organization.objects.first()
        context["field_list"] = [
            'name_eng',
            'abbrev',
            'province',
            'grouping',
            'regions',
        ]
        return context


#
class OrganizationDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/organization_detail.html'
    model = ml_models.Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name_eng',
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
            'dfo_contact_instructions',
            'notes',
            'grouping',
            'regions',
            'sectors',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class OrganizationUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/organization_form.html'
    model = ml_models.Organization
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_org = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:org_detail", kwargs={"pk": my_org.id}))


class OrganizationCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/organization_form.html'
    model = ml_models.Organization
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_org = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:org_detail", kwargs={"pk": my_org.id}))


class OrganizationDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/organization_confirm_delete.html'
    model = ml_models.Organization
    success_url = reverse_lazy('spot:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# MEMBER  (ORGANIZATION MEMBER) #
#################################
class MemberCreateView(SpotAccessRequiredMixin, CreateView):
    model = ml_models.OrganizationMember
    template_name = 'spot/member_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.MemberForm

    def get_initial(self):
        org = ml_models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = ml_models.Organization.objects.get(id=self.kwargs['org'])
        context['organization'] = org

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in ml_models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))


class MemberUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = ml_models.OrganizationMember
    template_name = 'spot/member_form_popout.html'
    form_class = forms.MemberForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in ml_models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class MemberDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/member_confirm_delete.html'
    model = ml_models.OrganizationMember
    success_url = reverse_lazy('spot:close_me')
    success_message = 'This member was successfully removed!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PERSON #
##########

class PersonListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/person_list.html'
    filterset_class = filters.PersonFilter
    model = ml_models.Person
    queryset = ml_models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'notes', 'id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = ml_models.Person.objects.first()
        context["field_list"] = [
            'display_name|Last name, First name',
            'phone_1',
            'email_1',
            'organizations',
        ]
        return context


class PersonDetailView(SpotAccessRequiredMixin, DetailView):
    model = ml_models.Person
    template_name = 'spot/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'first_name',
            'last_name',
            'phone_1',
            'phone_2',
            'fax',
            'email_1',
            'email_2',
            'notes',
            'last_modified_by',
        ]
        return context


class PersonUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = ml_models.Person
    template_name = 'spot/person_form_popout.html'

    form_class = forms.PersonForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("spot:person_detail", kwargs={"pk": self.kwargs["pk"]})


class PersonUpdateViewPopout(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/person_form_popout.html'
    model = ml_models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }


class PersonCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/person_form.html'
    model = ml_models.Person
    form_class = forms.PersonForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_person = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:person_detail", kwargs={"pk": my_person.id}))


class PersonCreateViewPopout(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/person_form_popout.html'
    model = ml_models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class PersonDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/person_confirm_delete.html'
    model = ml_models.Person
    success_url = reverse_lazy('spot:person_list')
    success_message = 'The person was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PROJECT #
###########

class ProjectListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/project_list.html'
    filterset_class = filters.ProjectFilter
    model = models.Project
    queryset = models.Project.objects.annotate(
        search_term=Concat('id', 'title', 'title_abbrev', 'program_reference_number', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Project.objects.first()
        context["field_list"] = [
            'id',
            'path_number',
            'program_reference_number',
            'status',
            'start_year',
            'program.abbrev_eng',
            'organization',
            'title',
            'regions',
        ]
        return context


#
class ProjectDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/project_detail.html'
    model = models.Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'path_number',
            'program_reference_number',
            'organization',
            'title',
            'program',
            'language',
            'status',
            'regions',
            'start_year',
            'project_length',
            'date_completed',
            'eccc_id',
        ]
        return context


class ProjectUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/project_form.html'
    model = models.Project
    form_class = forms.ProjectForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_project = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:project_detail", kwargs={"pk": my_project.id}))


class ProjectCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/project_form.html'
    model = models.Project
    form_class = forms.NewProjectForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_project = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:project_detail", kwargs={"pk": my_project.id}))


class ProjectDeleteView(SpotAdminRequiredMixin, DeleteView):
    template_name = 'spot/organization_confirm_delete.html'
    model = models.Project
    success_url = reverse_lazy('spot:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PROJECT PERSON #
##################
class ProjectPersonCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.ProjectPerson
    template_name = 'spot/project_person_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.ProjectPersonForm

    def get_initial(self):
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': my_project,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        context['project'] = my_project

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in ml_models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))


class ProjectPersonUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.ProjectPerson
    template_name = 'spot/project_person_form_popout.html'
    form_class = forms.ProjectPersonForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('spot:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get a list of people
        person_list = [
            '<a href="#" class="person_insert" code={id}>{first} {last}</a>'.format(
                id=p.id, first=p.first_name, last=p.last_name
            ) for p in ml_models.Person.objects.all()
        ]

        context['person_list'] = person_list

        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class ProjectPersonDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/project_person_confirm_delete.html'
    model = models.ProjectPerson
    success_url = reverse_lazy('spot:close_me')
    success_message = 'This contact was successfully removed!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PROJECT YEAR #
################

class ProjectYearDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/project_detail.html'
    model = models.Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'id',
            'path_number',
            'program_reference_number',
            'organization',
            'title',
            'program',
            'language',
            'status',
            'regions',
            'start_year',
            'project_length',
            'date_completed',
            'eccc_id',
        ]
        return context


class ProjectYearUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/project_form.html'
    model = models.Project
    form_class = forms.ProjectForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_project = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:project_detail", kwargs={"pk": my_project.id}))


class ProjectYearCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/project_form.html'
    model = models.Project
    form_class = forms.NewProjectForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_project = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:project_detail", kwargs={"pk": my_project.id}))


class ProjectYearDeleteView(SpotAdminRequiredMixin, DeleteView):
    template_name = 'spot/organization_confirm_delete.html'
    model = models.Project
    success_url = reverse_lazy('spot:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
