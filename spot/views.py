import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
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
from lib.functions.custom_functions import fiscal_year, listrify
from lib.functions.custom_functions import nz
from . import models
from . import forms
from . import filters
from . import emails
from . import reports


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'spot/close_me.html'


def in_spot_group(user):
    if user:
        return user.groups.filter(name='spot_access').count() != 0


class SpotAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

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
    model = models.Organization
    queryset = models.Organization.objects.annotate(
        search_term=Concat('name', 'id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Organization.objects.first()
        context["field_list"] = [
            'name',
            'province',
            'city',
            'address',
        ]
        return context


class OrganizationDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/organization_detail.html'
    model = models.Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
            'organization_type',
            'address',
            'province',
            'country',
            'city',
            'postal_code',
            'phone',
            'email',
            'website',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class OrganizationUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/organization_form.html'
    model = models.Organization
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_org = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:org_detail", kwargs={"pk": my_org.id}))


class OrganizationCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/organization_form.html'
    model = models.Organization
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_org = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:org_detail", kwargs={"pk": my_org.id}))


class OrganizationDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/organization_confirm_delete.html'
    model = models.Organization
    success_url = reverse_lazy('spot:org_list')
    success_message = 'The organization was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# PERSON #
##########
class PersonListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/person_list.html'
    filterset_class = filters.PersonFilter
    model = models.Person
    queryset = models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Person.objects.first()
        context["field_list"] = [
            'first_name',
            'last_name',
            'email',
            'province',
            'city',

        ]
        return context


class PersonDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Person
    template_name = 'spot/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'first_name',
            'last_name',
            'phone',
            'email',
            'city',
            'province',
            'address',
            'organizations',
            'role',
            'section',
            'other_membership',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class PersonUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.Person
    template_name = 'spot/person_form.html'
    form_class = forms.PersonForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("spot:person_detail", kwargs={"pk": self.kwargs["pk"]})


class PersonCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/person_form.html'
    model = models.Person
    form_class = forms.PersonForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_person = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:person_detail", kwargs={"pk": my_person.id}))


class PersonDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/person_confirm_delete.html'
    model = models.Person
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
        search_term=Concat('id', 'agreement_number', 'name', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Project.objects.first()
        context["field_list"] = [
            'agreement_number',
            'name',
            'region',
            'species',
            'DFO_project_authority',
        ]
        return context


class ProjectDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/project_detail.html'
    model = models.Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'agreement_number',
            'name',
            'project_description',
            'start_date',
            'end_date',
            'region',
            'ecosystem_type',
            'primary_river',
            'secondary_river',
            'lake_system',
            'watershed',
            'management_area',
            'smu_name',
            'cu_index',
            'cu_name',
            'species',
            'salmon_life_cycle',

            'project_stage',
            'project_type',
            'project_sub_type',
            'monitoring_approach',
            'project_theme',
            'core_component',
            'supportive_component',
            'project_purpose',
            'category_comments',

            'DFO_link',
            'DFO_program_reference',
            'government_organization',
            'government_reference',

            'DFO_project_authority',
            'DFO_area_chief',
            'DFO_aboriginal_AAA',
            'DFO_resource_manager',
            'tribal_council',
            'primary_first_nations_contact',
            'primary_first_nations_contact_role',
            'DFO_technicians',
            'contractor',
            'primary_contact_contractor',
            'partner',
            'primary_contact_partner',
            'date_last_modified',
            'last_modified_by',
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
    form_class = forms.ProjectForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_project = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:project_detail", kwargs={"pk": my_project.id}))


class ProjectDeleteView(SpotAdminRequiredMixin, DeleteView):
    template_name = 'spot/project_confirm_delete.html'
    model = models.Project
    success_url = reverse_lazy('spot:project_list')
    success_message = 'The project was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# OBJECTIVE #
###############
class ObjectiveListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/objective_list.html'
    filterset_class = filters.ObjectiveFilter
    model = models.Objective
    queryset = models.Objective.objects.annotate()
    search_term = Concat('number', 'id', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Objective.objects.first()
        context["field_list"] = [
            'project',
            'key_element',
            'activity',
            'location',
        ]
        return context


class ObjectiveDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Objective
    template_name = 'spot/objective_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'project',
            'task_description',
            'key_element',
            'activity',
            'element_title',
            'activity_title',
            'pst_requirement',
            'location',
            'objective_category',
            'species',
            'target_sample_number',
            'sample_type',
            'sil_requirement',
            'expected_results',
            'dfo_report',
            'outcome_deadline_met',
            'outcomes_contact',
            'outcomes_comment',
            'outcome_barrier',
            'capacity_building',
            'key_lesson',
            'missed_opportunities',
            'report_reference',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class ObjectiveUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/objective_form.html'
    model = models.Objective
    form_class = forms.ObjectiveForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_obj = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:obj_detail", kwargs={"pk": my_obj.id}))


class ObjectiveCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/objective_form.html'
    model = models.Objective
    form_class = forms.ObjectiveForm

    def get_initial(self):
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': my_project,
            'last_modified_by': self.request.user
        }

    def form_valid(self, form):
        my_obj = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:obj_detail", kwargs={"pk": my_obj.id}))


class ObjectiveDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/objective_confirm_delete.html'
    model = models.Objective
    success_message = 'The objective was deleted successfully!'

    def get_success_url(self):
        my_project = models.Objective.objects.get(pk=self.kwargs['pk']).project
        return reverse_lazy('spot:project_detail', kwargs={"pk": my_project.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# METHOD #
##########
class MethodListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/method_list.html'
    filterset_class = filters.MethodFilter
    model = models.Method
    queryset = models.Method.objects.annotate()
    search_term = Concat('doc_num', 'id', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Method.objects.first()
        context["field_list"] = [
            'project',
            'project_core_component',
            'planning_method_type',
            'field_work_method_type',
            'sample_processing_method_type',
            'data_entry_method_type',
            'data_analysis_method_type',
            'document_topic',
            'author',
            'publication_year',
            'reference_number',
            'publisher',
            'form_link',
        ]
        return context


class MethodDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Method
    template_name = 'spot/method_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'project',
            'planning_method_type',
            'field_work_method_type',
            'sample_processing_method_type',
            'data_entry_method_type',
            'data_analysis_method_type',
            'reporting_method_type',
            'scale_processing_location',
            'otolith_processing_location',
            'DNA_processing_location',
            'heads_processing_location',
            'instrument_data_processing_location',
            'shared_drive',
            'method_document_type',
            'authors',
            'publication_year',
            'title',
            'reference_number',
            'publisher',
            'document_link',
            'date_last_modified',
            'last_modified_by',

        ]
        return context


class MethodUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/method_form.html'
    model = models.Method
    form_class = forms.MethodForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        my_meth = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:meth_detail", kwargs={"pk": my_meth.id}))


class MethodCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/method_form.html'
    model = models.Method
    form_class = forms.MethodForm

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
        return context

    def form_valid(self, form):
        my_meth = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:meth_detail", kwargs={"pk": my_meth.id}))


class MethodDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/method_confirm_delete.html'
    model = models.Method
    success_message = 'The Method was deleted successfully!'

    def get_success_url(self):
        my_project = models.Method.objects.get(pk=self.kwargs['pk']).project
        return reverse_lazy('spot:project_detail', kwargs={"pk": my_project.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# DATABASES#
############
class DataListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/database_list.html'
    filterset_class = filters.DataFilter
    model = models.Data
    queryset = models.Data.objects.annotate()
    search_term = Concat('database', 'id', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Data.objects.first()
        context["field_list"] = [
            'project',
            'species_data',
            'samples_collected',
            'samples_collected_database',
            'sample_format',
            'data_products',
            'data_products_database',
            'data_programs',
        ]
        return context


class DataDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Data
    template_name = 'spot/database_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'project',
            'species_data',
            'samples_collected',
            'samples_collected_comment',
            'samples_collected_database',
            'samples',
            'sample_barrier',
            'sample_entered_database',
            'data_quality_check',
            'data_quality_person',
            'barrier_data_check_entry',
            'sample_format',
            'data_products',
            'data_products_database',
            'data_products_comment',
            'data_programs',
            'data_communication_recipient',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class DataUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/database_form.html'
    model = models.Data
    form_class = forms.DataForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:data_detail", kwargs={"pk": my_data.id}))


class DataCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/database_form.html'
    model = models.Data
    form_class = forms.DataForm

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
        return context

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:data_detail", kwargs={"pk": my_data.id}))


class DataDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/database_confirm_delete.html'
    model = models.Data
    success_message = 'The Database was deleted successfully!'

    def get_success_url(self):
        my_project = models.Data.objects.get(pk=self.kwargs['pk']).project
        return reverse_lazy('spot:project_detail', kwargs={"pk": my_project.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# FEEDBACK #
############
class FeedbackListView(SpotAdminRequiredMixin,FilterView):
    template_name = 'spot/feedback_list.html'
    filterset_class = filters.FeedbackFilter
    model = models.Feedback
    queryset = models.Feedback.objects.annotate()
    search_term = Concat('id', 'subject', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Feedback.objects.first()
        context["field_list"] = [
            'sent_by',
            'subject',
        ]
        return context


class FeedbackDetailView(SpotAdminRequiredMixin, DetailView):
    model = models.Feedback
    template_name = 'spot/feedback_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'subject',
            'comment',
            'sent_by',
        ]
        return context


class FeedbackCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/feedback_form.html'
    model = models.Feedback
    form_class = forms.FeedbackForm

    def get_initial(self):
        return {'sent_by': self.request.user}

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:feedback_detail", kwargs={"pk": my_data.id}))


class FeedbackDeleteView(SpotAdminRequiredMixin, DeleteView):
    template_name = 'spot/feedback_confirm_delete.html'
    model = models.Feedback
    success_url = reverse_lazy('spot:feedback_list')
    success_message = 'The Feedback was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# MEETINGS #
############
class MeetingsListView(SpotAccessRequiredMixin,FilterView):
    template_name = 'spot/meetings_list.html'
    filterset_class = filters.MeetingsFilter
    model = models.Meetings
    queryset = models.Meetings.objects.annotate()
    search_term = Concat('name', 'id', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Meetings.objects.first()
        context["field_list"] = [
            'name',
            'location',
        ]
        return context


class MeetingsDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Meetings
    template_name = 'spot/meetings_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
            'location',
            'description',
            'FN_communications',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class MeetingsCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/meetings_form.html'
    model = models.Meetings
    form_class = forms.MeetingsForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:meetings_detail", kwargs={"pk": my_data.id}))


class MeetingsUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/meetings_form.html'
    model = models.Meetings
    form_class = forms.MeetingsForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:meetings_detail", kwargs={"pk": my_data.id}))


class MeetingsDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/meetings_confirm_delete.html'
    model = models.Meetings
    success_url = reverse_lazy('spot:meetings_list')
    success_message = 'The Meeting was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# REPORTS #
###########
class ReportsListView(SpotAccessRequiredMixin,FilterView):
    template_name = 'spot/reports_list.html'
    filterset_class = filters.ReportsFilter
    model = models.Reports
    queryset = models.Reports.objects.annotate()
    search_term = Concat('report_topic', 'id', output_field=TextField())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Reports.objects.first()
        context["field_list"] = [
            'report_topic_program_level',
            'report_timeline',
            'report_purpose',
            'report_format_project_level',
            'report_client',
            'document_name',
            'document_author',
            'document_location',
            'document_link',
        ]
        return context


class ReportsDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Reports
    template_name = 'spot/reports_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'project',
            'report_timeline',
            'report_type',
            'report_concerns',
            'document_name',
            'document_author',
            'document_location',
            'document_reference_information',
            'document_link',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class ReportsCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/reports_form.html'
    model = models.Reports
    form_class = forms.ReportsForm

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
        return context

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:reports_detail", kwargs={"pk": my_data.id}))


class ReportsUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/reports_form.html'
    model = models.Reports
    form_class = forms.ReportsForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:reports_detail", kwargs={"pk": my_object.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class ReportsDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/reports_confirm_delete.html'
    model = models.Reports
    success_message = 'The Report was deleted successfully!'

    def get_success_url(self):
        my_project = models.Reports.objects.get(pk=self.kwargs['pk']).project
        return reverse_lazy('spot:project_detail', kwargs={"pk": my_project.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# Agreement History #
########
class AgreementHistoryCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.AgreementHistory
    template_name = 'spot/agreementhistory_form.html'
    form_class = forms.AgreementHistoryForm

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
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:agreementhistory_detail", kwargs={"pk": my_object.id}))


class AgreementHistoryUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.AgreementHistory
    template_name = 'spot/agreementhistory_form.html'
    form_class = forms.AgreementHistoryForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:agreementhistory_detail", kwargs={"pk": my_object.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class AgreementHistoryDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/agreementhistory_confirm_delete.html'
    model = models.AgreementHistory
    success_message = 'The Agreement History was successfully removed!'

    def get_success_url(self):
        my_project = models.AgreementHistory.objects.get(pk=self.kwargs['pk']).project
        return reverse_lazy('spot:project_detail', kwargs={"pk": my_project.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class AgreementHistoryDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.AgreementHistory
    template_name = 'spot/agreementhistory_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'history',
            'agreement_database',
            'agreement_status_comment',
            'funding_sources',
            'agreement_type',
            'project_lead_organization',
            'agreement_cost',
            'salmon_relevant_cost',
            'funding_years',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


# ObjectiveDataTypeQuality #
class ObjectiveDataTypeQualityCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.ObjectiveDataTypeQuality
    template_name = 'spot/objective_data_type_quality_popout.html'
    form_class = forms.ObjectiveDataTypeQualityForm

    def get_initial(self):
        my_objective = models.Objective.objects.get(pk=self.kwargs['obj'])
        return {
            'objective': my_objective,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_objective = models.Objective.objects.get(pk=self.kwargs['obj'])
        context['obj'] = my_objective
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class ObjectiveDataTypeQualityUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.ObjectiveDataTypeQuality
    template_name = 'spot/objective_data_type_quality_popout.html'
    form_class = forms.ObjectiveDataTypeQualityForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class ObjectiveDataTypeQualityDeleteView(SpotAccessRequiredMixin, DeleteView):
    model = models.ObjectiveDataTypeQuality
    success_message = 'The Sample Type was successfully removed!'
    template_name = 'spot/objective_data_type_quality_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('spot:close_me')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# OBJECTIVE OUTCOME #
class ObjectiveOutcomeCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.ObjectiveOutcome
    template_name = 'spot/objective_outcome_popout.html'
    form_class = forms.ObjectiveOutcomeForm

    def get_initial(self):
        my_objective = models.Objective.objects.get(pk=self.kwargs['obj'])
        return {
            'objective': my_objective,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_objective = models.Objective.objects.get(pk=self.kwargs['obj'])
        context['obj'] = my_objective
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class ObjectiveOutcomeUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.ObjectiveOutcome
    template_name = 'spot/objective_outcome_popout.html'
    form_class = forms.ObjectiveOutcomeForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class ObjectiveOutcomeDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/objective_outcome_confirm_delete.html'
    model = models.ObjectiveOutcome
    success_message = 'The Outcome was successfully removed!'

    def get_success_url(self):
        return reverse_lazy('spot:close_me')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# RIVER #
#########
class RiverListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/river_list.html'
    #filterset_class = filters.PersonFilter
    model = models.River
    queryset = models.River.objects.annotate(
        search_term=Concat('name', 'id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.River.objects.first()
        context["field_list"] = [
            'name',
            'latitude',
            'longitude',
        ]
        return context


class RiverDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.River
    template_name = 'spot/river_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
            'latitude',
            'longitude',
        ]
        return context


class RiverUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.River
    template_name = 'spot/river_form.html'
    form_class = forms.RiverForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("spot:river_detail", kwargs={"pk": self.kwargs["pk"]})


class RiverCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/river_form.html'
    model = models.River
    form_class = forms.RiverForm

    def form_valid(self, form):
        my_river = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:river_detail", kwargs={"pk": my_river.id}))


class RiverDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/river_confirm_delete.html'
    model = models.River
    success_url = reverse_lazy('spot:river_list')
    success_message = 'The River was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# Watershed #
#############
class WaterShedListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/watershed_list.html'
    #filterset_class = filters.PersonFilter
    model = models.Watershed
    queryset = models.Watershed.objects.annotate(
        search_term=Concat('name', 'id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Watershed.objects.first()
        context["field_list"] = [
            'name',
        ]
        return context


class WaterShedDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Watershed
    template_name = 'spot/watershed_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
        ]
        return context


class WaterShedUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.Watershed
    template_name = 'spot/watershed_form.html'
    form_class = forms.WatershedForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("spot:watershed_detail", kwargs={"pk": self.kwargs["pk"]})


class WaterShedCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/watershed_form.html'
    model = models.Watershed
    form_class = forms.WatershedForm

    def form_valid(self, form):
        my_watershed = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:watershed_detail", kwargs={"pk": my_watershed.id}))


class WaterShedDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/watershed_confirm_delete.html'
    model = models.Watershed
    success_url = reverse_lazy('spot:watershed_list')
    success_message = 'The Watershed was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# Lake System #
###############
class LakeSystemListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/lakesystem_list.html'
    #filterset_class = filters.PersonFilter
    model = models.LakeSystem
    queryset = models.LakeSystem.objects.annotate(
        search_term=Concat('name', 'id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.LakeSystem.objects.first()
        context["field_list"] = [
            'name',
        ]
        return context


class LakeSystemDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.LakeSystem
    template_name = 'spot/lakesystem_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
        ]
        return context


class LakeSystemUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.LakeSystem
    template_name = 'spot/lakesystem_form.html'
    form_class = forms.LakeSystemForm

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("spot:lakesystem_detail", kwargs={"pk": self.kwargs["pk"]})


class LakeSystemCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/lakesystem_form.html'
    model = models.LakeSystem
    form_class = forms.LakeSystemForm

    def form_valid(self, form):
        my_lakesystem = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:lakesystem_detail", kwargs={"pk": my_lakesystem.id}))


class LakeSystemDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/lakesystem_confirm_delete.html'
    model = models.LakeSystem
    success_url = reverse_lazy('spot:lakesystem_list')
    success_message = 'The Lake System was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)