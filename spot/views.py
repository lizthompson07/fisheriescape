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
from dm_apps.settings import MAPBOX_API_KEY
from . import emails
from django.http import HttpResponse
from django.db.models.deletion import ProtectedError


class IndexTemplateView(SpotAccessRequiredMixin, TemplateView):
    template_name = 'spot/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        river_list = []
        for project in models.Project.objects.all():
            for river in project.river.all():
                if river and river.name and river.latitude and river.longitude:
                    river_list.append([river.name, float(river.latitude), float(river.longitude)])
        context["river_markers"] = river_list
        return context

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
            'province_state',
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
            'is_active',
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
    error_message = 'The organization cannot be deleted'
    delete_protection = True

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(reverse_lazy('spot:org_list'))
        except ProtectedError:
            messages.error(self.request, self.error_message)
            return HttpResponseRedirect(reverse_lazy('spot:org_list'))


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
            'province_state',
            'city',
        ]
        return context


class PersonDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Person
    template_name = 'spot/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'is_active',
            'first_name',
            'last_name',
            'phone',
            'email',
            'city',
            'province_state',
            'country',
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
    error_message = 'Cannot delete person'
    delete_protection = True

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(reverse_lazy('spot:person_list'))
        except ProtectedError:
            messages.error(self.request, self.error_message)
            return HttpResponseRedirect(reverse_lazy('spot:person_list'))


# PROJECT #
###########
class ProjectListView(SpotAccessRequiredMixin, FilterView):
    template_name = 'spot/project_list.html'
    filterset_class = filters.ProjectFilter
    model = models.Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Project.objects.first()
        context["field_list"] = [
            'project_number',
            'agreement_number',
            'name',
            'area',
            'river',
            'species|Species',
            'DFO_project_authority',
            'funding_year|Funding Years'
        ]
        return context


class ProjectDetailView(SpotAccessRequiredMixin, DetailView):
    template_name = 'spot/project_detail.html'
    model = models.Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        markers = []
        for obj in self.object.river.all():
            if obj.latitude and obj.longitude:
                markers.append([obj.name, float(obj.latitude), float(obj.longitude)])
        context["river_markers"] = markers
        context['mapbox_api_key'] = MAPBOX_API_KEY
        context["field_list"] = [
            'project_number',
            'agreement_number',
            'agreement_history',
            'name',
            'project_description',
            'start_date',
            'end_date',

            'river',
            'other_species',
            'area',
            'ecosystem_type',
            'lake_system',
            'watershed',
            'other_site_info',
            'salmon_life_stage',
            'aquaculture_license_number',
            'water_license_number',
            'hatchery_name',
            'DFO_tenure',

            'project_stage',
            'project_type',
            'project_sub_type',
            'monitoring_approach',
            'project_theme',
            'core_component',
            'supportive_component',
            'project_purpose',
            'category_comments',

            # Place holder for header
            'project_links',

            'DFO_link',
            'DFO_program_reference',
            'government_organization',

            # Place holder for header
            'project_contacts',

            'DFO_project_authority',
            'DFO_area_chief',
            'DFO_IAA',
            'DFO_resource_manager',
            'funding_recipient',
            'first_nation',
            'contact',
            'contact_role',
            'DFO_technicians',
            'contractor',
            'contractor_contact',
            'partner',
            'partner_contact',

            # Place holder for header
            'costing',

            'agreement_database',
            'agreement_comment',
            'funding_sources',
            'other_funding_sources',
            'agreement_type',
            'lead_organization',

            # Place holder for header
            'funding_year',

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
        search_term=Concat('project', 'id', 'task_description', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Objective.objects.first()
        context["field_list"] = [
            'project',
            'element_title',
            'activity_title',
            'species|Species',
            'location',
            'sample_outcome|Sampling Outcome',
            'report_outcome|Reporting Outcome',
        ]
        return context


class ObjectiveDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Objective
    template_name = 'spot/objective_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'project',
            'unique_objective',
            'task_description',
            'element_title',
            'activity_title',

            'pst_requirement',
            'objective_category',
            'location',
            'sil_requirement',

            'sample_outcome_placeholder',

            'expected_results',
            'dfo_report',

            'reporting_outcome_placeholder',

            'outcomes_comment',

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
        objs = list(models.Objective.objects.all())
        num = 0
        for o in objs:
            if o.unique_objective:
                num = max(o.unique_objective)
                num = int(num) + 1
                num = str(num)
            else:
                num = None
        return {
            'project': my_project,
            'unique_objective': num,
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Method.objects.first()
        context["field_list"] = [
            'project',
            'area|Area',
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
            'unique_method_number',
            'planning_method_type',
            'field_work_method_type',
            'sample_processing_method_type',

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
        meths = list(models.Method.objects.all())
        num = 0
        for o in meths:
            if o.unique_method_number:
                num = max(o.unique_method_number)
                num = int(num) + 1
                num = str(num)
            else:
                num = None
        return {
            'project': my_project,
            'unique_method_number':num,
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
            'river|River',
            'species|Species',
            'samples_collected',
            'samples_collected_database',
            'sample_format',
            'data_products',
            'data_products_database',
        ]
        return context


class DataDetailView(SpotAccessRequiredMixin, DetailView):
    model = models.Data
    template_name = 'spot/data_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'project',
            'river',
            'samples_collected',
            'samples_collected_comment',
            'samples_collected_database',
            'shared_drive',
            'sample_barrier',
            'sample_entered_database',
            'data_quality_check',
            'sample_format',

            'data_products',
            'data_products_database',
            'data_products_comment',

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
        email = emails.FeedBackEmail(self.request, my_data)
        email.send()
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
    queryset = models.Reports.objects.annotate(search_term=Concat('project', 'document_name', output_field=TextField()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_object"] = models.Reports.objects.first()
        context["field_list"] = [
            'project',
            'area|Area',
            'river|River',
            'species|Species',
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


# sampleoutcome #
class SampleOutcomeCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.SampleOutcome
    template_name = 'spot/sample_outcome_popout.html'
    form_class = forms.SampleOutcomeForm

    def get_initial(self):
        my_objective = models.Objective.objects.get(pk=self.kwargs['obj'])

        return {
            'objective': my_objective,
            'unique_objective_number': my_objective.unique_objective,
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


class SampleOutcomeUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.SampleOutcome
    template_name = 'spot/sample_outcome_popout.html'
    form_class = forms.SampleOutcomeForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class SampleOutcomeDeleteView(SpotAccessRequiredMixin, DeleteView):
    model = models.SampleOutcome
    success_message = 'The Sample Type was successfully removed!'
    template_name = 'spot/sample_outcome_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('spot:close_me')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# REPORT OUTCOME #
class ReportOutcomeCreateView(SpotAccessRequiredMixin, CreateView):
    model = models.ReportOutcome
    template_name = 'spot/report_outcome_popout.html'
    form_class = forms.ReportOutcomeForm

    def get_initial(self):
        my_objective = models.Objective.objects.get(pk=self.kwargs['obj'])
        return {
            'objective': my_objective,
            'unique_objective_number': my_objective.unique_objective,
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


class ReportOutcomeUpdateView(SpotAccessRequiredMixin, UpdateView):
    model = models.ReportOutcome
    template_name = 'spot/report_outcome_popout.html'
    form_class = forms.ReportOutcomeForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy("spot:close_me"))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class ReportOutcomeDeleteView(SpotAccessRequiredMixin, DeleteView):
    template_name = 'spot/report_outcome_confirm_delete.html'
    model = models.ReportOutcome
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
    error_message = 'The River cannot be deleted'

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(reverse_lazy('spot:river_list'))
        except ProtectedError:
            messages.error(self.request, self.error_message)
            return HttpResponseRedirect(reverse_lazy('spot:river_list'))


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
    error_message = 'The Watershed cannot be deleted'

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(reverse_lazy('spot:watershed_list'))
        except ProtectedError:
            messages.error(self.request, self.error_message)
            return HttpResponseRedirect(reverse_lazy('spot:watershed_list'))


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
    error_message = 'The Lake System cannot be deleted'

    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(reverse_lazy('spot:lakesystem_list'))
        except ProtectedError:
            messages.error(self.request, self.error_message)
            return HttpResponseRedirect(reverse_lazy('spot:lakesystem_list'))


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
            'unique_method_number': my_method.unique_method_number,
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


class ProjectCloneView(ProjectUpdateView):
    template_name = 'spot/project_form.html'

    def get_h1(self):
        return "Cloning: " + str(self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloning"] = True
        return context

    def test_func(self):
        return self.request.user.is_authenticated

    def get_initial(self):
        obj = self.get_object()
        init = super().get_initial()
        init["agreement_number"] = f"CLONE OF: {obj.agreement_number}"
        init["project_number"] = f"CLONE OF: {obj.project_number}"
        init["cloning"] = True
        return init

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.Project.objects.get(pk=new_obj.pk)

        new_obj.project = new_obj
        new_obj.pk = None
        new_obj.save()

        for ah in old_obj.agreement_history.all():
            new_obj.agreement_history.add(ah)

        for r in old_obj.river.all():
            new_obj.river.add(r)

        for es in old_obj.ecosystem_type.all():
            new_obj.ecosystem_type.add(es)

        for ls in old_obj.lake_system.all():
            new_obj.lake_system.add(ls)

        for ws in old_obj.watershed.all():
            new_obj.watershed.add(ws)

        for ma in old_obj.management_area.all():
            new_obj.management_area.add(ma)

        for sls in old_obj.salmon_life_stage.all():
            new_obj.salmon_life_stage.add(sls)

        for hn in old_obj.hatchery_name.all():
            new_obj.hatchery_name.add(hn)

        for pst in old_obj.project_sub_type.all():
            new_obj.project_sub_type.add(pst)

        for pt in old_obj.project_theme.all():
            new_obj.project_theme.add(pt)

        for ma in old_obj.monitoring_approach.all():
            new_obj.monitoring_approach.add(ma)

        for cc in old_obj.core_component.all():
            new_obj.core_component.add(cc)

        for sc in old_obj.supportive_component.all():
            new_obj.supportive_component.add(sc)

        for pp in old_obj.project_purpose.all():
            new_obj.project_purpose.add(pp)

        for dpa in old_obj.DFO_project_authority.all():
            new_obj.DFO_project_authority.add(dpa)

        for dac in old_obj.DFO_area_chief.all():
            new_obj.DFO_area_chief.add(dac)

        for daa in old_obj.DFO_IAA.all():
            new_obj.DFO_IAA.add(daa)

        for drm in old_obj.DFO_resource_manager.all():
            new_obj.DFO_resource_manager.add(drm)

        for dt in old_obj.DFO_technicians.all():
            new_obj.DFO_technicians.add(dt)

        for part in old_obj.partner.all():
            new_obj.partner.add(part)

        for pc in old_obj.partner_contact.all():
            new_obj.partner_contact.add(pc)

        for fs in old_obj.funding_sources.all():
            new_obj.funding_sources.add(fs)

        return HttpResponseRedirect(reverse_lazy("spot:project_detail", kwargs={"pk": new_obj.project.id}))


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
