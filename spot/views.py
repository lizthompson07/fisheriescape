import csv
from datetime import date

from django.contrib import messages
from django.db.models import TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView, TemplateView
from django_filters.views import FilterView

from shared_models.views import CommonFormsetView, CommonHardDeleteView
from . import filters
from . import forms
from . import models
from .mixins import SuperuserOrAdminRequiredMixin, SpotAccessRequiredMixin, SpotAdminRequiredMixin


class IndexTemplateView(SpotAccessRequiredMixin, TemplateView):
    template_name = 'spot/index.html'


# ORGANIZATION #
################
class OrganizationListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/organization_list.html'
    filterset_class = filters.OrganizationFilter
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
            'section',
            'address',
            'province_state',
            'country',
            'city',
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
            'province_state',
            'country,'
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
        search_term=Concat('id', 'agreement_number', 'name', 'project_description', output_field=TextField()))

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
            'project_number',
            'agreement_number',
            'agreement_history',
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

            'stock_management_unit',
            'cu_index',
            'cu_name',
            'species',
            'salmon_life_stage',

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
            'policy_program_connection',

            'DFO_project_authority',
            'DFO_area_chief',
            'DFO_aboriginal_AAA',
            'DFO_resource_manager',
            'first_nation',
            'first_nations_contact',
            'first_nations_contact_role',
            'DFO_technicians',
            'contractor',
            'contractor_contact',
            'partner',
            'partner_contact',

            'agreement_database',
            'agreement_comment',
            'funding_sources',
            'other_funding_sources',
            'agreement_type',
            'lead_organization',

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
    queryset = models.Objective.objects.annotate(
        search_term=Concat('project', 'id', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Objective.objects.first()
        context["field_list"] = [
            'project',
            'element_title',
            'activity_title',
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
            'element_title',
            'activity_title',

            'pst_requirement',
            'location',
            'objective_category',
            'species',
            'sil_requirement',

            'expected_results',
            'dfo_report',

            'outcome_met',
            'outcomes_contact',
            'outcomes_comment',
            'outcome_barrier',
            'capacity_building',
            'key_lesson',
            'missed_opportunities',

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
    queryset = models.Method.objects.annotate(
    search_term = Concat('project', 'knowledge_consideration', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Method.objects.first()
        context["field_list"] = [
            'project',
            'planning_method_type',
            'field_work_method_type',
            'sample_processing_method_type',
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
            'knowledge_consideration',
            'scale_processing_location',
            'otolith_processing_location',
            'DNA_processing_location',
            'heads_processing_location',
            'instrument_data_processing_location',

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


# DATA#
############
class DataListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/data_list.html'
    filterset_class = filters.DataFilter
    model = models.Data
    queryset = models.Data.objects.annotate(
    search_term = Concat('project', 'data_products_comment', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Data.objects.first()
        context["field_list"] = [
            'project',
            'species',
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
    template_name = 'spot/data_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'project',
            'species',
            'samples_collected',
            'samples_collected_comment',
            'samples_collected_database',
            'shared_drive',
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
            'data_communication',
            'date_last_modified',
            'last_modified_by',
        ]
        return context


class DataUpdateView(SpotAccessRequiredMixin, UpdateView):
    template_name = 'spot/data_form.html'
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
    template_name = 'spot/data_form.html'
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
    template_name = 'spot/data_confirm_delete.html'
    model = models.Data
    success_message = 'The Data was deleted successfully!'

    def get_success_url(self):
        my_project = models.Data.objects.get(pk=self.kwargs['pk']).project
        return reverse_lazy('spot:project_detail', kwargs={"pk": my_project.id})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# FEEDBACK #
############
class FeedbackListView(SpotAdminRequiredMixin, FilterView):
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
    queryset = models.Reports.objects.annotate(
    search_term = Concat('project', 'document_name', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Reports.objects.first()
        context["field_list"] = [
            'report_timeline',
            'report_type',
            'document_name',
            'document_author',
            'document_reference_information',
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
            'document_reference_information',
            'document_link',
            'published',
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


# Funding Year #
class FundingYearCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.FundingYears
    template_name = 'spot/funding_year_popout.html'
    form_class = forms.FundingYearForm

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
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class FundingYearUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.FundingYears
    template_name = 'spot/funding_year_popout.html'
    form_class = forms.FundingYearForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class FundingYearDeleteView(SpotAccessRequiredMixin, DeleteView):
    model = models.FundingYears
    success_message = 'The Funding Year was successfully removed!'
    template_name = 'spot/funding_year_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('spot:close_me')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# Method Document #
class MethodDocumentCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.MethodDocument
    template_name = 'spot/method_document_popout.html'
    form_class = forms.MethodDocumentForm

    def get_initial(self):
        my_method = models.Method.objects.get(pk=self.kwargs['meth'])
        return {
            'method': my_method,
            'last_modified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_method = models.Method.objects.get(pk=self.kwargs['meth'])
        context['method'] = my_method
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class MethodDocumentUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.MethodDocument
    template_name = 'spot/method_document_popout.html'
    form_class = forms.MethodDocumentForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class MethodDocumentDeleteView(SpotAccessRequiredMixin, DeleteView):
    model = models.MethodDocument
    success_message = 'The Document was successfully removed!'
    template_name = 'spot/method_document_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('spot:close_me')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


### PROJECT CERTIFICATION ###
class ProjectCertifiedCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.ProjectCertified
    template_name = 'spot/project_certified_popout.html'
    form_class = forms.ProjectCertifiedForm

    def get_initial(self):
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': my_project,
            'certified_by': self.request.user
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_project = models.Project.objects.get(pk=self.kwargs['project'])
        context['project'] = my_project
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))


class ProjectCertifiedUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.ProjectCertified
    template_name = 'spot/project_certified_popout.html'
    form_class = forms.ProjectCertifiedForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))

    def get_initial(self):
        return {
            'certified_by': self.request.user
        }


class ProjectCertifiedDeleteView(SpotAccessRequiredMixin, DeleteView):
    model = models.ProjectCertified
    success_message = 'The Project Certification was successfully removed!'
    template_name = 'spot/project_certified_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('spot:close_me')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


#EXPORT#
##############
def export_project(request):
    project = models.Project.objects.all()
    project_filter = filters.ProjectFilter(request.GET, queryset=project).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=project' + str(date.today()) + '.csv'

    writer = csv.writer(response, delimiter=',')
    writer.writerow([
        'project_number',
        'agreement_number',
        'agreement_history',
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

        'stock_management_unit',
        'cu_index',
        'cu_name',
        'species',
        'salmon_life_stage',

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
        'policy_program_connection',

        'DFO_project_authority',
        'DFO_area_chief',
        'DFO_aboriginal_AAA',
        'DFO_resource_manager',
        'first_nation',
        'first_nations_contact',
        'first_nations_contact_role',
        'DFO_technicians',
        'contractor',
        'contractor_contact',
        'partner',
        'partner_contact',

        'agreement_database',
        'agreement_comment',
        'funding_sources',
        'other_funding_sources',
        'agreement_type',
        'lead_organization',

        'date_last_modified',
        'last_modified_by',

    ])

    for obj in project_filter:
        writer.writerow([
            obj.agreement_number,
            obj.project_number,
            ",".join(i.name for i in obj.agreement_history.all()),
            obj.name,
            obj.project_description,
            obj.start_date,
            obj.end_date,

            obj.region,
            obj.ecosystem_type,
            obj.primary_river,
            ",".join(i.name for i in obj.secondary_river.all()),
            ",".join(i.name for i in obj.lake_system.all()),
            ",".join(i.name for i in obj.watershed.all()),
            obj.management_area,

            obj.stock_management_unit,
            obj.cu_index,
            obj.cu_name,
            ",".join(i.name for i in obj.species.all()),
            ",".join(i.name for i in obj.salmon_life_stage.all()),

            obj.project_stage,
            obj.project_type,
            ",".join(i.name for i in obj.project_sub_type.all()),
            obj.monitoring_approach,
            ",".join(i.name for i in obj.project_theme.all()),
            ",".join(i.name for i in obj.core_component.all()),
            ",".join(i.name for i in obj.supportive_component.all()),
            ",".join(i.name for i in obj.project_purpose.all()),
            obj.category_comments,

            obj.DFO_link,
            obj.DFO_program_reference,
            obj.government_organization,
            obj.policy_program_connection,

            ",".join(i.full_name for i in obj.DFO_project_authority.all()),
            ",".join(i.full_name for i in obj.DFO_area_chief.all()),
            ",".join(i.full_name for i in obj.DFO_aboriginal_AAA.all()),
            ",".join(i.full_name for i in obj.DFO_resource_manager.all()),
            obj.first_nation,
            obj.first_nations_contact,
            obj.first_nations_contact_role,
            ",".join(i.full_name for i in obj.DFO_technicians.all()),
            obj.contractor,
            obj.contractor_contact,
            ",".join(i.name for i in obj.partner.all()),
            ",".join(i.full_name for i in obj.partner_contact.all()),

            obj.agreement_database,
            obj.agreement_comment,
            ",".join(i.name for i in obj.funding_sources.all()),
            obj.other_funding_sources,
            obj.agreement_type,
            obj.lead_organization,

            obj.date_last_modified,
            obj.last_modified_by,
        ])

    return response


def export_objective(request):
    objective = models.Objective.objects.all()
    objective_filter = filters.ObjectiveFilter(request.GET, queryset=objective).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=objective' + str(date.today()) + '.csv'

    writer = csv.writer(response, delimiter=',')
    writer.writerow([
        'project',
        'objective_id',
        'task_description',
        'element_title',
        'pst_requirement',
        'location',
        'objective_category',
        'species',
        'sil_requirement',
        'expected_results',
        'dfo_report',
        'outcome_met',
        'outcomes_contact',
        'outcome_barrier',
        'capacity_building',
        'key_lesson',
        'missed_opportunities',
        'date_last_modified',
        'last_modified_by',

    ])

    for obj in objective_filter:
        writer.writerow([
            obj.project,
            obj.objective_id,
            obj.task_description,
            obj.element_title,
            obj.pst_requirement,
            ",".join(i.name for i in obj.location.all()),
            ",".join(i.name for i in obj.objective_category.all()),
            ",".join(i.name for i in obj.species.all()),
            obj.sil_requirement,
            obj.expected_results,
            obj.dfo_report,
            obj.outcome_met,
            obj.outcomes_contact,
            ",".join(i.name for i in obj.outcome_barrier.all()),
            ",".join(i.name for i in obj.capacity_building.all()),
            obj.key_lesson,
            obj.missed_opportunities,
            obj.date_last_modified,
            obj.last_modified_by

        ])
    return response


def export_data(request):
    data = models.Data.objects.all()
    data_filter = filters.DataFilter(request.GET, queryset=data).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=data' + str(date.today()) + '.csv'

    writer = csv.writer(response, delimiter=',')
    writer.writerow([
        'project',
        'species',
        'samples_collected',
        'samples_collected_comment',
        'samples_collected_database',
        'shared_drive',
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
        'data_communication',
        'date_last_modified',
        'last_modified_by',

    ])

    for obj in data_filter:
        writer.writerow([
            obj.project,
            ",".join(i.name for i in obj.species.all()),
            ",".join(i.name for i in obj.samples_collected.all()),
            obj.samples_collected_comment,
            obj.shared_drive,
            ",".join(i.name for i in obj.sample_barrier.all()),
            obj.sample_entered_database,
            obj.data_quality_check,
            obj.data_quality_person,
            ",".join(i.name for i in obj.barrier_data_check_entry.all()),
            ",".join(i.name for i in obj.sample_format.all()),
            ",".join(i.name for i in obj.data_products.all()),
            ",".join(i.name for i in obj.data_products_database.all()),
            obj.data_products_comment,
            ",".join(i.name for i in obj.data_programs.all()),
            ",".join(i.name for i in obj.data_communication.all()),
            obj.date_last_modified,
            obj.last_modified_by,

        ])
    return response


def export_method(request):
    method = models.Method.objects.all()
    data_filter = filters.MethodFilter(request.GET, queryset=method).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=method' + str(date.today()) + '.csv'

    writer = csv.writer(response, delimiter=',')
    writer.writerow([
        'field_work_method_type',
        'planning_method_type',
        'sample_processing_method_type',
        'knowledge_consideration',
        'scale_processing_location',
        'otolith_processing_location',
        'DNA_processing_location',
        'heads_processing_location',
        'instrument_data_processing_location',
        'date_last_modified',
        'last_modified_by',
    ])

    for obj in data_filter:
        writer.writerow([
            ",".join(i.name for i in obj.field_work_method_type.all()),
            ",".join(i.name for i in obj.planning_method_type.all()),
            ",".join(i.name for i in obj.sample_processing_method_type.all()),
            obj.knowledge_consideration,
            obj.scale_processing_location,
            obj.otolith_processing_location,
            obj.DNA_processing_location,
            obj.heads_processing_location,
            obj.instrument_data_processing_location,
            obj.date_last_modified,
            obj.last_modified_by,
        ])
    return response


def export_reports(request):
    reports = models.Reports.objects.all()
    reports_filter = filters.ReportsFilter(request.GET, queryset=reports).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=reports' + str(date.today()) + '.csv'

    writer = csv.writer(response, delimiter=',')
    writer.writerow([
        'project',
        'report_timeline',
        'report_type',
        'report_concerns',
        'document_name',
        'document_author',
        'document_reference_information',
        'document_link',
        'published',
        'date_last_modified',
        'last_modified_by',

    ])

    for obj in reports_filter:
        writer.writerow([
            obj.project,
            obj.report_timeline,
            obj.report_type,
            obj.report_concerns,
            obj.document_name,
            obj.document_author,
            obj.document_reference_information,
            obj.document_link,
            obj.published,
            obj.date_last_modified,
            obj.last_modified_by,

        ])
    return response


class SpotUserFormsetView(SuperuserOrAdminRequiredMixin, CommonFormsetView):
    template_name = 'shared_models/generic_formset.html'
    h1 = "Manage Spot Users"
    queryset = models.SpotUser.objects.all()
    formset_class = forms.SpotUserFormset
    success_url_name = "spot:manage_spot_users"
    home_url_name = "spot:index"
    delete_url_name = "spot:delete_spot_user"
    container_class = "container bg-light curvy"


class SpotUserHardDeleteView(SuperuserOrAdminRequiredMixin, CommonHardDeleteView):
    model = models.SpotUser
    success_url = reverse_lazy("spot:manage_spot_users")
