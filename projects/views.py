import datetime
import os
import pandas as pd
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
from easy_pdf.views import PDFTemplateView
from lib.functions.fiscal_year import fiscal_year
from lib.functions.nz import nz
from . import models
from . import forms
from . import filters
from . import reports

project_field_list = [
    'project_title',
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
        context['next_fiscal_year'] = fiscal_year(next=True)
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
            'section',
            'program',
            'budget_code',
            'date_last_modified',
            'last_modified_by',
        ]

        context["field_list_1"] = [
            'description',
            'priorities',
            'deliverables',
        ]

        salary_total = 0
        om_total = 0
        gc_total = 0
        capital_total = 0

        # first calc for staff
        for staff in project.staff_members.all():
            # exclude full time employees
            if staff.employee_type.id != 1 or staff.employee_type.id != 6:
                # if salary
                if staff.employee_type.cost_type is 1:
                    salary_total += nz(staff.cost, 0)
                # if o&M
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


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Project
    login_url = '/accounts/login_required/'
    form_class = forms.ProjectForm

    def get_initial(self):
        my_dict = {
            'last_modified_by': self.request.user,
        }

        try:
            my_dict["start_date"] = "{}-{:02d}-{:02d}".format(self.object.start_date.year, self.object.start_date.month,
                                                              self.object.start_date.day)
        except:
            print("no start date...")

        try:
            my_dict["end_date"] = "{}-{:02d}-{:02d}".format(self.object.end_date.year, self.object.end_date.month,
                                                            self.object.end_date.day)
        except:
            print("no start date...")

        return my_dict


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
    success_message = _('The project was successfully deleted!')
    login_url = '/accounts/login_required/'

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
        if form.cleaned_data["save_then_go_OT"] == "1":
            return HttpResponseRedirect(reverse_lazy('projects:ot_calc', kwargs={"pk": object.id}))
        else:
            return HttpResponseRedirect(reverse('projects:close_me'))


class StaffUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Staff
    template_name = 'projects/staff_form_popout.html'
    form_class = forms.StaffForm
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def staff_delete(request, pk):
    object = models.Staff.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The staff member has been successfully deleted from project."))
    return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))


class OverTimeCalculatorTemplateView(LoginRequiredMixin, UpdateView):
    login_url = '/accounts/login_required/'
    template_name = 'projects/overtime_calculator_popout.html'
    form_class = forms.OTForm
    model = models.Staff

    def get_initial(self):
        return {
            # 'weekdays': 0,
            # 'saturdays': 0,
            # 'sundays': 0,
            # 'stat_holidays': 0,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # create a pandas date_range object for upcoming fiscal year
        target_year = pd.datetime.today().year
        start = "{}-04-01".format(target_year)
        end = "{}-03-31".format(target_year + 1)
        datelist = pd.date_range(start=start, end=end).tolist()
        context['datelist'] = datelist

        # send in the upcoming fiscal year string
        context["next_fiscal_year"] = fiscal_year(next=True)

        # send in a list of stat holidays from: https://www.tpsgc-pwgsc.gc.ca/remuneration-compensation/services-paye-pay-services/paye-centre-pay/feries-holidays-eng.html
        stat_holiday_list = [
            # Good Friday
            datetime.datetime.strptime("April 19, 2019", "%B %d, %Y"),
            # Easter Monday
            datetime.datetime.strptime("April 22, 2019", "%B %d, %Y"),
            # Victoria Day
            datetime.datetime.strptime("May 20, 2019", "%B %d, %Y"),
            # Canada Day
            datetime.datetime.strptime("July 1, 2019", "%B %d, %Y"),
            # Labour Day
            datetime.datetime.strptime("September 2, 2019", "%B %d, %Y"),
            # Thanksgiving Day
            datetime.datetime.strptime("October 14, 2019", "%B %d, %Y"),
            # Remembrance Day
            datetime.datetime.strptime("November 11, 2019", "%B %d, %Y"),
            # Christmas Day
            datetime.datetime.strptime("December 25, 2019", "%B %d, %Y"),
            # Boxing Day
            datetime.datetime.strptime("December 26, 2019", "%B %d, %Y"),
        ]
        context["stat_holiday_list"] = stat_holiday_list
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('projects:staff_edit', kwargs={"pk": object.id}))


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
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def collaborator_delete(request, pk):
    object = models.Collaborator.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The collaborator has been successfully deleted from project."))
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
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def agreement_delete(request, pk):
    object = models.CollaborativeAgreement.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The agreement has been successfully deleted."))
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
    login_url = '/accounts/login_required/'

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_type'] = _("O&M")
        return context


def om_cost_delete(request, pk):
    object = models.OMCost.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The cost has been successfully deleted."))
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
    login_url = '/accounts/login_required/'

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
    messages.success(request, _("The cost has been successfully deleted."))
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
    login_url = '/accounts/login_required/'

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
    messages.success(request, _("The cost has been successfully deleted."))
    return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": object.project.id}))


# REPORTS #
###########

class ReportSearchFormView(LoginRequiredMixin, FormView):
    template_name = 'projects/report_search.html'
    login_url = '/accounts/login_required/'
    form_class = forms.ReportSearchForm

    def get_initial(self):
        # default the year to the year of the latest samples
        return {"fiscal_year": fiscal_year(next=True)}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        fiscal_year = str(form.cleaned_data["fiscal_year"])
        report = int(form.cleaned_data["report"])

        if report == 1:
            return HttpResponseRedirect(reverse("projects:report_master", kwargs={'fiscal_year': fiscal_year}))


def master_spreadsheet(request, fiscal_year, user=None):
    # my_site = models.Site.objects.get(pk=site)
    file_url = reports.generate_master_spreadsheet(fiscal_year, user)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="Science project planning MASTER LIST {}.xlsx"'.format(
                fiscal_year)
            return response
    raise Http404


# USER #
########

# this is a complicated cookie. Therefore we will not use a model view or model form and handle the clean data manually.
class UserCreateView(LoginRequiredMixin, FormView):
    form_class = forms.UserCreateForm
    template_name = 'projects/user_form.html'
    login_url = '/accounts/login_required/'

    def get_success_url(self):
        return reverse_lazy('projects:close_me')

    def form_valid(self, form):
        # retrieve data from form
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email1']

        # create a new user
        User.objects.create(
            username=email,
            first_name=first_name,
            last_name=last_name,
            password="pbkdf2_sha256$120000$ctoBiOUIJMD1$DWVtEKBlDXXHKfy/0wKCpcIDYjRrKfV/wpYMHKVrasw=",
            is_active=1,
            email=email,
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
