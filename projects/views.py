from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.db.models import Value, TextField, Q
from django.db.models.functions import Concat
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import Context, loader
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
###
from easy_pdf.views import PDFTemplateView

from accounts import models as accounts_models
from collections import OrderedDict

from lib.functions.nz import nz
from . import models
from . import forms
from . import filters
from . import emails

project_field_list = [
    'project_title',
    'division',
    'section',
    'program',
    'budget_code',
    'status',
    'approved',
    'start_date',
    'end_date',
    'description',
    'priorities',
    'deliverables',
    'data_collection',
    'data_sharing',
    'data_storage',
    'metadata_url',
    'regional_dm',
    'regional_dm_needs',
    'sectional_dm',
    'sectional_dm_needs',
    'vehicle_needs',
    'it_needs',
    'chemical_needs',
    'ship_needs',
    'date_last_modified',
    'last_modified_by',
]


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'projects/close_me.html'


class IndexTemplateView(TemplateView):
    template_name = 'projects/index.html'


# PROJECTS #
############
class MyProjectListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    template_name = 'projects/my_project_list.html'

    def get_queryset(self):
        return models.Staff.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = models.Staff.objects.filter(user=self.request.user)

        weeks_total = 0
        for obj in projects:
            weeks_total += nz(obj.duration_weeks, 0)

        context["weeks_total"] = weeks_total

        return context


class MySectionListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login_required/'
    template_name = 'projects/my_section_list.html'

    def get_queryset(self):
        return models.Section.objects.filter(section_head=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProjectListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'projects/project_list.html'
    model = models.Project
    filterset_class = filters.ProjectFilter


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = models.Project
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context["field_list"] = [
            'project_title',
            'division',
            'section',
            'program',
            'budget_code',
            'date_last_modified',
            'last_modified_by',
        ]

        salary_total = 0
        om_total = 0
        gc_total = 0
        capital_total = 0

        # first calc for staff
        for staff in project.staff_members.all():
            # exclude full time employees
            if staff.employee_type.id != 1 or staff.employee_type.id != 6:
                if staff.employee_type.cost_type is 1:
                    salary_total += nz(staff.cost, 0)
                elif staff.employee_type.cost_type is 2:
                    om_total += nz(staff.cost, 0)

        # O&M costs
        for cost in project.om_costs.all():
            om_total += nz(cost.budget_requested, 0)

        # Capital costs
        for cost in project.capital_costs.all():
            capital_total += nz(cost.budget_requested, 0)

        # g&c costs
        for cost in project.gc_costs.all():
            gc_total += nz(cost.budget_requested, 0)

        context["salary_total"] = salary_total
        context["om_total"] = om_total
        context["gc_total"] = gc_total
        context["capital_total"] = capital_total

        can_delete = False
        if self.request.user.is_superuser:
            can_delete = True
        else:
            for staff in project.staff_members.filter(employee_type_id=1):
                try:
                    if staff.user.id is self.request.user.id:
                        can_delete = True
                        break
                except:
                    print("staff has no user id")

        context["can_delete"] = can_delete
        return context


class ProjectPrintDetailView(LoginRequiredMixin, PDFTemplateView):
    model = models.Project
    login_url = '/accounts/login_required/'
    template_name = "projects/project_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(pk=self.kwargs["pk"])
        context["object"] = project
        context["field_list"] = project_field_list

        salary_total = 0
        om_total = 0
        gc_total = 0
        capital_total = 0

        # first calc for staff
        for staff in project.staff_members.all():
            # exclude full time employees
            if staff.employee_type.id != 1 or staff.employee_type.id != 6:
                if staff.employee_type.cost_type is 1:
                    salary_total += nz(staff.cost, 0)
                elif staff.employee_type.cost_type is 2:
                    om_total += nz(staff.cost, 0)

        # O&M costs
        for cost in project.om_costs.all():
            om_total += nz(cost.budget_requested, 0)

        # Capital costs
        for cost in project.capital_costs.all():
            capital_total += nz(cost.budget_requested, 0)

        # g&c costs
        for cost in project.gc_costs.all():
            gc_total += nz(cost.budget_requested, 0)

        context["salary_total"] = salary_total
        context["om_total"] = om_total
        context["gc_total"] = gc_total
        context["capital_total"] = capital_total
        return context

        # def get_pdf_filename(self):
        #     site = models.Site.objects.get(pk=self.kwargs['site']).site
        #     return "{} Annual Report {}.pdf".format(self.kwargs['year'], site)
        #
        # def get_context_data(self, **kwargs):
        #     reports.generate_annual_watershed_report(self.kwargs["site"], self.kwargs["year"])
        #     site = models.Site.objects.get(pk=self.kwargs['site']).site
        #     return super().get_context_data(
        #         pagesize="A4 landscape",
        #         title="Annual Report for {}_{}".format(site, self.kwargs['year']),
        #         **kwargs
        #     )

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Project
    login_url = '/accounts/login_required/'
    form_class = forms.ProjectForm

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ProjectSubmitUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Project
    login_url = '/accounts/login_required/'
    form_class = forms.ProjectSubmitForm
    template_name = "projects/project_submit_form.html"

    def get_initial(self):
        if self.object.submitted:
            submit = False
        else:
            submit = True

        return {
            'last_modified_by': self.request.user,
            'submitted': submit,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context["field_list"] = project_field_list

        salary_total = 0
        om_total = 0
        gc_total = 0
        capital_total = 0

        # first calc for staff
        for staff in project.staff_members.all():
            # exclude full time employees
            if staff.employee_type.id != 1 or staff.employee_type.id != 6:
                if staff.employee_type.cost_type is 1:
                    salary_total += nz(staff.cost, 0)
                elif staff.employee_type.cost_type is 2:
                    om_total += nz(staff.cost, 0)

        # O&M costs
        for cost in project.om_costs.all():
            om_total += nz(cost.budget_requested, 0)

        # Capital costs
        for cost in project.capital_costs.all():
            capital_total += nz(cost.budget_requested, 0)

        # g&c costs
        for cost in project.gc_costs.all():
            gc_total += nz(cost.budget_requested, 0)

        context["salary_total"] = salary_total
        context["om_total"] = om_total
        context["gc_total"] = gc_total
        context["capital_total"] = capital_total

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = models.Project
    login_url = '/accounts/login_required/'
    form_class = forms.NewProjectForm

    def form_valid(self, form):
        object = form.save()
        models.Staff.objects.create(project=object, employee_type_id=1, user_id=self.request.user.id)

        for obj in models.OMCategory.objects.all():
            new_item = models.OMCost.objects.create(project=object, om_category=obj)
            new_item.save()

        return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.id}))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Project
    permission_required = "__all__"
    success_url = reverse_lazy('projects:my_project_list')
    success_message = 'The project was successfully deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# STAFF #
#########

class StaffCreateView(LoginRequiredMixin, CreateView):
    model = models.Staff
    template_name = 'projects/staff_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.StaffForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class StaffUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Staff
    template_name = 'projects/staff_form_popout.html'
    form_class = forms.StaffForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def staff_delete(request, pk):
    object = models.Staff.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The staff member has been successfully deleted from project.")
    return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))


# COLLABORATOR #
################

class CollaboratorCreateView(LoginRequiredMixin, CreateView):
    model = models.Collaborator
    template_name = 'projects/collaborator_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.CollaboratorForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class CollaboratorUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Collaborator
    template_name = 'projects/collaborator_form_popout.html'
    form_class = forms.CollaboratorForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def collaborator_delete(request, pk):
    object = models.Collaborator.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The collaborator has been successfully deleted from project.")
    return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))


# AGREEMENTS #
##############

class AgreementCreateView(LoginRequiredMixin, CreateView):
    model = models.CollaborativeAgreement
    template_name = 'projects/agreement_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.AgreementForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class AgreementUpdateView(LoginRequiredMixin, UpdateView):
    model = models.CollaborativeAgreement
    template_name = 'projects/agreement_form_popout.html'
    form_class = forms.AgreementForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def agreement_delete(request, pk):
    object = models.CollaborativeAgreement.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The agreement has been successfully deleted.")
    return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))


# OM COSTS #
############

class OMCostCreateView(LoginRequiredMixin, CreateView):
    model = models.OMCost
    template_name = 'projects/cost_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.OMCostForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        context['cost_type'] = "O&M"
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class OMCostUpdateView(LoginRequiredMixin, UpdateView):
    model = models.OMCost
    template_name = 'projects/cost_form_popout.html'
    form_class = forms.OMCostForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_type'] = "O&M"
        return context


def om_cost_delete(request, pk):
    object = models.OMCost.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The cost has been successfully deleted.")
    return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))


# CAPITAL COSTS #
#################

class CapitalCostCreateView(LoginRequiredMixin, CreateView):
    model = models.CapitalCost
    template_name = 'projects/cost_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.CapitalCostForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        context['cost_type'] = "Capital"
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class CapitalCostUpdateView(LoginRequiredMixin, UpdateView):
    model = models.CapitalCost
    template_name = 'projects/cost_form_popout.html'
    form_class = forms.CapitalCostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_type'] = "Capital"
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def capital_cost_delete(request, pk):
    object = models.CapitalCost.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The cost has been successfully deleted.")
    return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))


# GC COSTS #
############

class GCCostCreateView(LoginRequiredMixin, CreateView):
    model = models.GCCost
    template_name = 'projects/cost_form_popout.html'
    login_url = '/accounts/login_required/'
    form_class = forms.GCCostForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        context['cost_type'] = "G&C"
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class GCCostUpdateView(LoginRequiredMixin, UpdateView):
    model = models.GCCost
    template_name = 'projects/cost_form_popout.html'
    form_class = forms.GCCostForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_type'] = "G&C"
        return context


def gc_cost_delete(request, pk):
    object = models.GCCost.objects.get(pk=pk)
    object.delete()
    messages.success(request, "The cost has been successfully deleted.")
    return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))
