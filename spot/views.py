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
    model = models.Organization #ml_
    queryset = models.Organization.objects.annotate(
        search_term=Concat('name', 'id', output_field=TextField())) #ml_

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Organization.objects.first() #ml_
        context["field_list"] = [
            'name',
            'province',
            'city',
            'address',
        ]
        return context


class OrganizationDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/organization_detail.html'
    model = models.Organization #ml_

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
    model = models.Organization #ml_
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_org = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:org_detail", kwargs={"pk": my_org.id}))


class OrganizationCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/organization_form.html'
    model = models.Organization #ml_
    form_class = forms.OrganizationForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_org = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:org_detail", kwargs={"pk": my_org.id}))


class OrganizationDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/organization_confirm_delete.html'
    model = models.Organization #ml_
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
    model = models.Person #ml_
    queryset = models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'id', output_field=TextField())) #ml_

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Person.objects.first() #ml_
        context["field_list"] = [
            'first_name',
            'last_name',
            'email',
            'province',
            'city',

        ]
        return context


class PersonDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Person #ml_
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
    model = models.Person #ml_
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
    model = models.Person #ml_
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
            'agreement_database',
            'agreement_status',
            'agreement_status_comment',
            'funding_sources',
            'funding_years',
            'name',
            'project_description',
            'start_date',
            'end_date',
            'region',
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
            'project_type',
            'project_sub_type',
            'project_stage',
            'project_scale',
            'monitoring_approach',
            'project_theme',
            'core_component',
            'supportive_component',
            'category_comments',
            'DFO_link',
            'DFO_program_reference',
            'government_organization',
            'government_reference',
            'strategic_agreement_link',
            'DFO_project_authority',
            'DFO_aboriginal_AAA',
            'DFO_resource_manager',
            'tribal_council',
            'primary_first_nations_contact',
            'primary_first_nations_contact_role',
            'FN_relationship_level',
            'other_first_nations_contact',
            'other_first_nations_contact_role',
            'DFO_technicians',
            'third_party_organization',
            'primary_third_party_contact',
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
            'number',
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
            'number',
            'work_plan_section',
            'task_description',
            'key_element',
            'activity',
            'element_title',
            'activity_title',
            'pst_requirement',
            'location',
            'objective_category',
            'duration',
            'species',
            'target_sample_num',
            'sample_type',
            'salmon_stage',
            'sil_requirement',
            'expected_results',
            'dfo_report',
            'scientific_outcome',
            'outcomes_category',
            'outcomes_deadline',
            'outcomes_contact',
            'data_quality_type',
            'data_quality_level',
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
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_obj = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:obj_detail", kwargs={"pk": my_obj.id}))


class ObjectiveDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/objective_confirm_delete.html'
    model = models.Objective
    success_url = reverse_lazy('spot:obj_list')
    success_message = 'The objective was deleted successfully!'

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
            'project_core_component',
            'planning_method_type',
            'field_work_method_type',
            'sample_processing_method_type',
            'data_entry_method_type',
            'data_analysis_method_type',
            'reporting_method_type',
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

    def form_valid(self, form):
        my_meth = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:meth_detail", kwargs={"pk": my_meth.id}))


class MethodCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/method_form.html'
    model = models.Method
    form_class = forms.MethodForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_meth = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:meth_detail", kwargs={"pk": my_meth.id}))


class MethodDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/method_confirm_delete.html'
    model = models.Method
    success_url = reverse_lazy('spot:meth_list')
    success_message = 'The Method was deleted successfully!'

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
            'species_data',
            'database',
            'primary_data_contact',
            'data_format',
            'data_program',
            'data_program',
            'data_quality_type',
            'data_quality_level',
        ]
        return context


class DataDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Data
    template_name = 'spot/database_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'species_data',
            'data_type',
            'data_subtype',
            'data_type_comment',
            'sample_types_included',
            'primary_data_contact',
            'database',
            'data_program',
            'data_format',
            'data_quality_type',
            'data_quality_level',
            'DFO_analysts',
            'non_DFO_analysts',
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

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:data_detail", kwargs={"pk": my_data.id}))


class DataCreateView(SpotAccessRequiredMixin, CreateView):
    template_name = 'spot/database_form.html'
    model = models.Data
    form_class = forms.DataForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:data_detail", kwargs={"pk": my_data.id}))


class DataDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/database_confirm_delete.html'
    model = models.Data
    success_url = reverse_lazy('spot:data_list')
    success_message = 'The Database was deleted successfully!'

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
            'report_timeline',
            'report_type',
            'report_topic_program_level',
            'report_format_project_level',
            'report_format_program_level',
            'fishery_support_link',
            'report_problem_addressed_content',
            'report_purpose',
            'report_client',
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
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:reports_detail", kwargs={"pk": my_data.id}))


class ReportsUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/reports_form.html'
    model = models.Reports
    form_class = forms.ReportsForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}

    def form_valid(self, form):
        my_data = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:reports_detail", kwargs={"pk": my_data.id}))


class ReportsDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/reports_confirm_delete.html'
    model = models.Reports
    success_url = reverse_lazy('spot:reports_list')
    success_message = 'The Report was deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
