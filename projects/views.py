import datetime
import json
import os
from collections import OrderedDict
from copy import deepcopy

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Sum, Q, Count, Value
from django.shortcuts import render
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView, FormView, TemplateView
from easy_pdf.views import PDFTemplateView
from lib.functions.custom_functions import fiscal_year, listrify
from lib.functions.custom_functions import nz
from . import models
from . import forms
from . import emails
from . import filters
from . import reports
from . import stat_holidays
from shared_models import models as shared_models


def get_help_text_dict():
    my_dict = {}
    for obj in models.HelpText.objects.all():
        my_dict[obj.field_name] = str(obj)

    return my_dict
    #
    # help_text_dict = {
    #     "user": _("This field should be used if the staff member is a DFO employee (as opposed to the 'Person name' field)"),
    #     "start_date": _("This is the start date of the project, not the fiscal year"),
    #     "is_negotiable": _("Is this program a part of DFO's core mandate?"),
    #     "is_competitive": _("For example, is the funding for this project coming from a program like ACRDP, PARR, SPERA, etc.?"),
    #     "priorities": _("What will be the project emphasis in this particular fiscal year?"),
    #     "deliverables": _("Please provide this information in bulleted form, if possible."),
    # }


def in_projects_admin_group(user):
    """
    Will return True if user is in project_admin group
    """
    if user:
        return user.groups.filter(name='projects_admin').count() != 0


def is_management_or_admin(user):
    """
        Will return True if user is in project_admin group, or if user is listed as a head of a section, division or branch
    """
    if user.id:
        if in_projects_admin_group(user) or \
                shared_models.Section.objects.filter(head=user).count() > 0 or \
                shared_models.Division.objects.filter(head=user).count() > 0 or \
                shared_models.Branch.objects.filter(head=user).count() > 0:
            return True


def is_section_head(user, project):
    try:
        return True if project.section.head == user else False
    except AttributeError as e:
        print(e)


def is_division_manager(user, project):
    try:
        return True if project.section.division.head == user else False
    except AttributeError:
        pass


def is_rds(user, project):
    try:
        return True if project.section.division.branch.head == user else False
    except AttributeError:
        pass


def can_modify_project(user, project_id):
    """
    returns True if user has permissions to delete or modify a project

    The answer of this question will depend on whether the project is submitted. Project leads cannot edit a submitted project
    """
    if user.id:
        project = models.Project.objects.get(pk=project_id)

        # check to see if a superuser or projects_admin -- both are allow to modify projects
        if "projects_admin" in [g.name for g in user.groups.all()]:
            return True

        # check to see if they are a section head, div. manager or RDS
        if is_section_head(user, project) or is_division_manager(user, project) or is_rds(user, project):
            return True

        # if the project is unsubmitted, the project lead is also able to edit the project... obviously
        # check to see if they are a project lead
        if not project.submitted and \
                user in [staff.user for staff in project.staff_members.filter(lead=True)]:
            return True


def is_admin_or_project_manager(user, project):
    """returns True if user is either in 'projects_admin' group OR if they are a manager of the project (section head, div. manager, RDS)"""
    if user.id:

        # check to see if a superuser or projects_admin -- both are allow to modify projects
        if "projects_admin" in [g.name for g in user.groups.all()]:
            return True

        # check to see if they are a section head, div. manager or RDS
        if is_section_head(user, project) or is_division_manager(user, project) or is_rds(user, project):
            return True


class ProjectLeadRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        try:
            obj = self.get_object()
        except AttributeError:
            project_id = self.kwargs.get("project")
        else:
            try:
                project_id = getattr(obj, "project").id
            except AttributeError:
                project_id = obj.id
        finally:
            return can_modify_project(self.request.user, project_id)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return in_projects_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_section_heads_only'))
        return super().dispatch(request, *args, **kwargs)


class ManagerOrAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        return is_management_or_admin(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_section_heads_only'))
        return super().dispatch(request, *args, **kwargs)


class CanModifyProjectRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login_required/'

    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        try:
            obj = self.get_object()
        except AttributeError:
            project_id = self.kwargs.get("project")
        else:
            try:
                project_id = getattr(obj, "project").id
            except AttributeError:
                project_id = obj.id
        finally:
            return can_modify_project(self.request.user, project_id)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))
        return super().dispatch(request, *args, **kwargs)


def financial_summary_data(project):
    # for every funding source, we will want to summarize: Salary, O&M, Capital and TOTAL
    my_dict = OrderedDict()

    for fs in project.get_funding_sources():
        my_dict[fs] = {}
        my_dict[fs]["salary"] = 0
        my_dict[fs]["om"] = 0
        my_dict[fs]["capital"] = 0
        my_dict[fs]["total"] = 0

        # first calc for staff
        for staff in project.staff_members.filter(funding_source=fs):
            # exclude any employees that should be excluded. This is a fail safe since the form should prevent data entry
            if not staff.employee_type.exclude_from_rollup:
                if staff.employee_type.cost_type == 1:
                    my_dict[fs]["salary"] += nz(staff.cost, 0)
                elif staff.employee_type.cost_type == 2:
                    my_dict[fs]["om"] += nz(staff.cost, 0)

        # O&M costs
        for cost in project.om_costs.filter(funding_source=fs):
            my_dict[fs]["om"] += nz(cost.budget_requested, 0)

        # Capital costs
        for cost in project.capital_costs.filter(funding_source=fs):
            my_dict[fs]["capital"] += nz(cost.budget_requested, 0)

    # do the totals. I am doing this loop as separate so that the total entry comes at the end of all the funding sources
    my_dict["total"] = {}
    my_dict["total"]["salary"] = 0
    my_dict["total"]["om"] = 0
    my_dict["total"]["capital"] = 0
    my_dict["total"]["total"] = 0
    for fs in project.get_funding_sources():
        my_dict[fs]["total"] = float(my_dict[fs]["capital"]) + float(my_dict[fs]["salary"]) + float(my_dict[fs]["om"])
        my_dict["total"]["salary"] += my_dict[fs]["salary"]
        my_dict["total"]["om"] += my_dict[fs]["om"]
        my_dict["total"]["capital"] += my_dict[fs]["capital"]
        my_dict["total"]["total"] += my_dict[fs]["total"]

    return my_dict


def multiple_projects_financial_summary(project_list):
    my_dict = {}

    # first, get the list of funding sources
    funding_sources = []
    for project in project_list:
        funding_sources.extend(project.get_funding_sources())
    funding_sources = list(set(funding_sources))
    funding_sources_order = ["{} {}".format(fs.funding_source_type, fs.tname) for fs in funding_sources]
    for fs in [x for _, x in sorted(zip(funding_sources_order, funding_sources))]:
        my_dict[fs] = {}
        my_dict[fs]["salary"] = 0
        my_dict[fs]["om"] = 0
        my_dict[fs]["capital"] = 0
        my_dict[fs]["total"] = 0
        for project in project_list.all():
            # first calc for staff
            for staff in project.staff_members.filter(funding_source=fs):
                # exclude any employees that should be excluded. This is a fail safe since the form should prevent data entry
                if not staff.employee_type.exclude_from_rollup:
                    if staff.employee_type.cost_type == 1:
                        my_dict[fs]["salary"] += nz(staff.cost, 0)
                    elif staff.employee_type.cost_type == 2:
                        my_dict[fs]["om"] += nz(staff.cost, 0)
            # O&M costs
            for cost in project.om_costs.filter(funding_source=fs):
                my_dict[fs]["om"] += nz(cost.budget_requested, 0)
            # Capital costs
            for cost in project.capital_costs.filter(funding_source=fs):
                my_dict[fs]["capital"] += nz(cost.budget_requested, 0)

    my_dict["total"] = {}
    my_dict["total"]["salary"] = 0
    my_dict["total"]["om"] = 0
    my_dict["total"]["capital"] = 0
    my_dict["total"]["total"] = 0
    for fs in funding_sources:
        my_dict[fs]["total"] = float(my_dict[fs]["capital"]) + float(my_dict[fs]["salary"]) + float(my_dict[fs]["om"])
        my_dict["total"]["salary"] += my_dict[fs]["salary"]
        my_dict["total"]["om"] += my_dict[fs]["om"]
        my_dict["total"]["capital"] += my_dict[fs]["capital"]
        my_dict["total"]["total"] += my_dict[fs]["total"]

    return my_dict


project_field_list = [
    'id',
    'year',
    'section',
    'project_title',
    'activity_type',
    'functional_group',
    'default_funding_source',
    'funding_sources|{}'.format(_("Complete list of funding sources")),
    # 'programs',
    'tags',
    'is_national',
    'status',
    'is_competitive',
    'is_approved',
    'start_date',
    'end_date',
    'description',
    'priorities',
    'deliverables',
    'data_collection',
    'data_sharing',
    'data_storage',
    'metadata_url',
    'regional_dm_needs',
    'sectional_dm_needs',
    'vehicle_needs',
    'it_needs',
    'chemical_needs',
    'ship_needs',
    'coding|Known financial coding',
    'last_modified_by',
    'date_last_modified',
]

gulf_field_list = deepcopy(project_field_list)
gulf_field_list.remove("is_competitive")
gulf_field_list.remove("is_approved")
gulf_field_list.remove("metadata_url")
gulf_field_list.remove("regional_dm_needs")
gulf_field_list.remove("sectional_dm_needs")


def get_section_choices(all=False, full_name=True):
    if full_name:
        my_attr = "full_name"
    else:
        my_attr = _("name")

    return [(s.id, getattr(s, my_attr)) for s in
            shared_models.Section.objects.all().order_by(
                "division__branch__region",
                "division__branch",
                "division",
                "name"
            ) if s.projects.count() > 0] if not all else [(s.id, getattr(s, my_attr)) for s in
                                                          shared_models.Section.objects.filter(
                                                              division__branch__name__icontains="science").order_by(
                                                              "division__branch__region",
                                                              "division__branch",
                                                              "division",
                                                              "name"
                                                          )]


def get_division_choices(all=False):
    if all:
        division_list = set([shared_models.Section.objects.get(pk=s[0]).division for s in get_section_choices(all=True)])
    else:
        division_list = set([shared_models.Section.objects.get(pk=s[0]).division for s in get_section_choices()])
    q_objects = Q()  # Create an empty Q object to start with
    for d in division_list:
        q_objects |= Q(id=d.id)  # 'or' the Q objects together

    return [(d.id, str(d)) for d in
            shared_models.Division.objects.filter(q_objects).order_by(
                "branch__region",
                "name"
            )]


def get_region_choices(all=False):
    if all:
        region_list = set([shared_models.Division.objects.get(pk=d[0]).branch.region for d in get_division_choices(all=True)])
    else:
        region_list = set([shared_models.Division.objects.get(pk=d[0]).branch.region for d in get_division_choices()])
    q_objects = Q()  # Create an empty Q object to start with
    for r in region_list:
        q_objects |= Q(id=r.id)  # 'or' the Q objects together

    return [(r.id, str(r)) for r in
            shared_models.Region.objects.filter(q_objects).order_by(
                "name",
            )]


# Create your views here.
class CloserTemplateView(TemplateView):
    template_name = 'projects/close_me.html'


class IndexTemplateView(TemplateView):
    template_name = 'projects/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_id_list = []
        if self.request.user.id:
            if self.request.user.groups.filter(name="projects_admin").count() > 0:
                section_id_list = [project.section_id for project in models.Project.objects.all()]
                section_list = shared_models.Section.objects.filter(id__in=section_id_list)
            else:
                # are they section heads?
                section_id_list.extend([section.id for section in self.request.user.shared_models_sections.all()])

                # are they a division manager?
                if self.request.user.shared_models_divisions.count() > 0:
                    for division in self.request.user.shared_models_divisions.all():
                        for section in division.sections.all():
                            section_id_list.append(section.id)

                # are they an RDS?
                if self.request.user.shared_models_branches.count() > 0:
                    for branch in self.request.user.shared_models_branches.all():
                        for division in branch.divisions.all():
                            for section in division.sections.all():
                                section_id_list.append(section.id)

                section_id_set = set([s for s in section_id_list if shared_models.Section.objects.get(pk=s).projects.count() > 0])
                section_list = shared_models.Section.objects.filter(id__in=section_id_set)
            context["section_list"] = section_list

        # messages.warning(self.request,
        #               mark_safe(_("<b class='red-font blink-me'>PLEASE NOTE: This database is currently being updated. Please refrain from entering new data until this message is no longer present from the home page.</b>")))

        return context


# PROJECTS #
############
class MyProjectListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'projects/my_project_list.html'
    filterset_class = filters.MyProjectFilter

    def get_queryset(self):
        return models.Project.objects.filter(staff_members__user=self.request.user).order_by("-year", "project_title")

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"year": fiscal_year(next=True, sap_style=True)}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object_list = context.get("object_list")
        fy = object_list.first().year if object_list.count() > 0 else None

        staff_instances = self.request.user.staff_instances.filter(project__year=fy)
        context['fte_approved_projects'] = staff_instances.filter(
            project__approved=True, project__submitted=True
        ).aggregate(dsum=Sum("duration_weeks"))["dsum"]

        context['fte_unapproved_projects'] = staff_instances.filter(
            project__approved=False, project__submitted=True
        ).aggregate(dsum=Sum("duration_weeks"))["dsum"]
        context['fte_unsubmitted_projects'] = staff_instances.filter(
            project__submitted=False
        ).aggregate(dsum=Sum("duration_weeks"))["dsum"]
        context['fy'] = fy

        context["project_list"] = models.Project.objects.filter(
            id__in=[s.project.id for s in self.request.user.staff_instances.all()]
        )

        context["project_field_list"] = [
            "year",
            "submitted|{}".format("Submitted"),
            "approved",
            "section|Section",
            "project_title",
            "is_hidden|is this a hidden project?",
            "is_lead|{}?".format("Are you a project lead"),
            "status_report|{}".format("Status reports"),
        ]

        return context


class SectionListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'projects/section_project_list.html'
    filterset_class = filters.SectionFilter

    def get_queryset(self):
        return models.Project.objects.filter(section_id=self.kwargs.get("section")).order_by('-year', 'section__division', 'section',
                                                                                             'project_title')

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"year": fiscal_year(next=True, sap_style=True)}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["field_list"] = [
            "project_title",
            "functional_group",
            "default_funding_source",
            "activity_type",
            "project_leads|{}".format("Leads"),
            "meeting_notes",
        ]

        object_list = context.get("object_list")
        fy = object_list.first().year if object_list.count() > 0 else None
        context['next_fiscal_year'] = shared_models.FiscalYear.objects.get(pk=fiscal_year(next=True, sap_style=True))
        context['unapproved_projects'] = object_list.filter(approved=False, submitted=True)
        context['unsubmitted_projects'] = object_list.filter(submitted=False)

        approved_projects = object_list.filter(approved=True, submitted=True)
        context['approved_projects'] = approved_projects

        # need to create a dict for displaying projects by funding source.
        fs_dict = {}
        funding_sources = set([project.default_funding_source for project in approved_projects])
        for fs in funding_sources:
            fs_dict[fs] = approved_projects.filter(default_funding_source=fs)
        context['fs_dict'] = fs_dict

        # need to create a dict for displaying projects by functional group.
        fg_dict = {}
        functional_groups = set([project.functional_group for project in approved_projects])
        for fg in functional_groups:
            fg_dict[fg] = approved_projects.filter(functional_group=fg)
        context['fg_dict'] = fg_dict

        # need to create a dict for displaying projects by activity type.
        at_dict = {}
        activity_types = set([project.activity_type for project in approved_projects])
        for at in activity_types:
            at_dict[at] = approved_projects.filter(activity_type=at)
        context['at_dict'] = at_dict

        # need to create a staff list dictionary
        user_dict = {}

        user_list = list(set([staff.user for project in object_list for staff in project.staff_members.all() if staff.user]))
        user_sort_order = [str(user) if user else "AAA" for user in user_list]
        for user in [x for _, x in sorted(zip(user_sort_order, user_list))]:
            user_dict[user] = {}
            user_dict[user]["qs"] = user.staff_instances.filter(
                project__year=fy
            ).order_by("project__submitted", "project__approved", "lead", "project__project_title")

            user_dict[user]["fte_approved"] = user.staff_instances.filter(
                project__approved=True, project__submitted=True, project__year=fy
            ).aggregate(dsum=Sum("duration_weeks"))["dsum"]

            user_dict[user]["fte_unapproved"] = user.staff_instances.filter(
                project__approved=False, project__submitted=True, project__year=fy
            ).aggregate(dsum=Sum("duration_weeks"))["dsum"]

            user_dict[user]["fte_unsubmitted"] = user.staff_instances.filter(
                project__submitted=False, project__year=fy
            ).aggregate(dsum=Sum("duration_weeks"))["dsum"]

            user_dict[user]["fte_total"] = user.staff_instances.filter(
                project__year=fy
            ).aggregate(dsum=Sum("duration_weeks"))["dsum"]

        context['user_dict'] = user_dict

        # financials
        context['financials_dict'] = multiple_projects_financial_summary(object_list)

        return context


class MySectionListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'projects/my_section_list.html'
    filterset_class = filters.MySectionFilter

    def get_queryset(self):
        return models.Project.objects.filter(section__head=self.request.user).order_by('-year', 'section__division', 'section',
                                                                                       'project_title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fy_form'] = forms.FYForm(user=self.request.user.id)

        context['type'] = _("section")
        context['next_fiscal_year'] = shared_models.FiscalYear.objects.get(pk=fiscal_year(next=True, sap_style=True))
        context['has_section'] = models.Project.objects.filter(section__head=self.request.user).count() > 0
        return context


class ProjectListView(LoginRequiredMixin, FilterView):
    login_url = '/accounts/login_required/'
    template_name = 'projects/project_list.html'
    queryset = models.Project.objects.filter(
        is_hidden=False, submitted=True,
    ).order_by('-year', 'section__division', 'section', 'project_title')
    filterset_class = filters.ProjectFilter


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = models.Project
    login_url = '/accounts/login_required/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        # If this is a gulf region project, only show the gulf region fields
        if project.section.division.branch.region.id == 1:
            context["field_list"] = gulf_field_list
        else:
            context["field_list"] = project_field_list

        context["files"] = project.files.all()
        context["financial_summary_dict"] = financial_summary_data(project)

        # Determine if the user will be able to edit the project.
        context["can_edit"] = can_modify_project(self.request.user, project.id)
        context["is_lead"] = self.request.user in [staff.user for staff in project.staff_members.filter(lead=True)]
        return context


class ProjectOverviewDetailView(ProjectDetailView):

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return 'projects/project_overview_pop.html'
        else:
            return 'projects/project_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProjectPrintDetailView(LoginRequiredMixin, PDFTemplateView):
    model = models.Project
    login_url = '/accounts/login_required/'
    template_name = "projects/project_report.html"

    def get_pdf_filename(self):
        project = models.Project.objects.get(pk=self.kwargs["pk"])
        pdf_filename = "{}-{}-{}-{}-{}.pdf".format(
            project.year.id,
            project.section.division.abbrev,
            project.section.abbrev,
            project.id,
            str(project.project_title).title().replace(" ", "")[:10],
        )

        return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(pk=self.kwargs["pk"])
        context["report_mode"] = True
        context["object"] = project
        context["field_list"] = project_field_list

        # bring in financial summary data
        my_context = financial_summary_data(project)
        context = {**my_context, **context}

        return context


class ProjectUpdateView(CanModifyProjectRequiredMixin, UpdateView):
    model = models.Project
    form_class = forms.ProjectForm
    template_name = 'projects/project_form_popout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()
        return context

    def get_initial(self):
        my_dict = {
            'last_modified_by': self.request.user,
        }

        try:
            my_dict["start_date"] = "{}-{:02d}-{:02d}".format(self.object.start_date.year, self.object.start_date.month,
                                                              self.object.start_date.day)
        except Exception as e:
            print("no start date...")

        try:
            my_dict["end_date"] = "{}-{:02d}-{:02d}".format(self.object.end_date.year, self.object.end_date.month,
                                                            self.object.end_date.day)
        except Exception as e:
            print("no end date...")

        return my_dict

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse("shared_models:close_me"))


class ProjectSubmitUpdateView(CanModifyProjectRequiredMixin, UpdateView):
    model = models.Project
    form_class = forms.ProjectSubmitForm

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return "projects/project_action_form_popout.html"
        else:
            return "projects/project_submit_form.html"

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
        project = self.get_object()

        if self.kwargs.get("pop"):
            action = _("Un-submit Project") if self.object.submitted else _("Submit Project")
            context["action"] = action
            btn_color = "danger" if self.object.submitted else "success"
            context["btn_color"] = btn_color

        # If this is a gulf region project, only show the gulf region fields
        if project.section.division.branch.region.id == 1:
            context["field_list"] = gulf_field_list
        else:
            context["field_list"] = project_field_list

        context["report_mode"] = True

        # bring in financial summary data
        my_context = financial_summary_data(project)
        context = {**my_context, **context}

        return context

    def form_valid(self, form):
        my_object = form.save()

        # if this is a popout, it is a manager or admin doing the submission and no email is needed
        if self.kwargs.get("pop"):
            return HttpResponseRedirect(reverse('projects:close_me'))
        else:
            # Send out an email only when a project is submitted
            if my_object.submitted:
                # create a new email object
                email = emails.ProjectSubmissionEmail(self.object)
                # send the email object
                if settings.PRODUCTION_SERVER:
                    send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                              recipient_list=email.to_list, fail_silently=False, )
                else:
                    print(email)
            messages.success(self.request,
                             _("The project was submitted and an email has been sent to notify the section head!"))
            return super().form_valid(form)


class ProjectNotesUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
    model = models.Project
    form_class = forms.ProjectNotesForm
    template_name = "projects/project_action_form_popout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        action = _("Save")
        context["action"] = action
        btn_color = "primary"
        context["btn_color"] = btn_color

        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class ProjectApprovalUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
    model = models.Project
    template_name = "projects/project_action_form_popout.html"
    success_url = reverse_lazy("projects:close_me")
    form_class = forms.ProjectApprovalForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        action = _("Un-approve") if self.object.approved else _("Approve")
        context["action"] = action
        btn_color = "danger" if self.object.submitted else "success"
        context["btn_color"] = btn_color
        return context

    def form_valid(self, form):
        my_object = form.save(commit=False)
        if my_object.approved:
            my_object.approved = False
        else:
            my_object.approved = True
        my_object.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = models.Project
    login_url = '/accounts/login_required/'
    form_class = forms.NewProjectForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()

        # here are the option objects we want to send in through context
        # only from the science branches of each region

        division_dict = {}
        for d in get_division_choices(all=True):
            my_division = shared_models.Division.objects.get(pk=d[0])
            division_dict[my_division.id] = {}
            division_dict[my_division.id]["display"] = "{} - {}".format(
                getattr(my_division.branch, _("name")),
                getattr(my_division, _("name")),
            )
            division_dict[my_division.id]["region_id"] = my_division.branch.region_id

        section_dict = {}
        for s in get_section_choices(all=True):
            my_section = shared_models.Section.objects.get(pk=s[0])
            section_dict[my_section.id] = {}
            section_dict[my_section.id]["display"] = str(my_section)
            section_dict[my_section.id]["division_id"] = my_section.division_id
        context['division_json'] = json.dumps(division_dict)
        context['section_json'] = json.dumps(section_dict)

        return context

    def form_valid(self, form):
        my_object = form.save()
        models.Staff.objects.create(project=my_object, lead=True, employee_type_id=1, user_id=self.request.user.id,
                                    funding_source=my_object.default_funding_source)

        for obj in models.OMCategory.objects.all():
            new_item = models.OMCost.objects.create(project=my_object, om_category=obj, funding_source=my_object.default_funding_source)
            new_item.save()

        return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": my_object.id}))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ProjectDeleteView(CanModifyProjectRequiredMixin, DeleteView):
    model = models.Project
    success_message = _('The project was successfully deleted!')

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return "projects/project_action_form_popout.html"
        else:
            return "projects/project_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        if self.kwargs.get("pop"):
            return reverse('projects:close_me')
        else:
            return reverse_lazy('projects:my_project_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get("pop"):
            context["delete_message"] = _("Are you certain you want to delete this project? <br><br> This action is permanent.")
            context["action"] = _("Delete")
            context["btn_color"] = "danger"
        return context


class ProjectCloneUpdateView(ProjectUpdateView):
    def test_func(self):
        if self.request.user.id:
            return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:denied_access'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        my_object = models.Project.objects.get(pk=self.kwargs["pk"])
        init = super().get_initial()
        init["project_title"] = "CLONE OF: {}".format(my_object.project_title)
        init["year"] = fiscal_year(sap_style=True, next=True)
        # init["created_by"] = self.request.user
        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloned"] = True
        return context

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.Project.objects.get(pk=new_obj.pk)
        new_programs = form.cleaned_data.get("programs")
        new_tags = form.cleaned_data.get("tags")
        new_obj.pk = None
        new_obj.submitted = False
        new_obj.approved = False
        new_obj.date_last_modified = timezone.now()
        new_obj.last_modified_by = self.request.user
        new_obj.save()

        # now that the new object has an id, we can add the many 2 many links
        for p in new_programs:
            new_obj.programs.add(p.id)

        for t in new_tags:
            new_obj.tags.add(t.id)

        # Now we need to replicate all the related records:
        # 1) staff
        for old_rel_obj in old_obj.staff_members.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project = new_obj
            new_rel_obj.save()

        # we have to just make sure that the user is a lead on the project. Otherwise they will not be able to edit.
        my_staff, created = models.Staff.objects.get_or_create(
            user=self.request.user,
            project=new_obj,
            employee_type_id=1,
        )
        my_staff.lead = True
        my_staff.save()

        # 2) O&M
        for old_rel_obj in old_obj.om_costs.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project = new_obj
            new_rel_obj.save()

        # 3) Capital
        for old_rel_obj in old_obj.capital_costs.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project = new_obj
            new_rel_obj.save()

        # 4) G&C
        for old_rel_obj in old_obj.gc_costs.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project = new_obj
            new_rel_obj.save()

        # 5) Collaborators and Partners
        for old_rel_obj in old_obj.collaborators.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project = new_obj
            new_rel_obj.save()

        # 6) Collaborative Agreements
        for old_rel_obj in old_obj.agreements.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project = new_obj
            new_rel_obj.save()

        # 7) Milestones
        for old_rel_obj in old_obj.milestones.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project = new_obj
            new_rel_obj.save()

        return HttpResponseRedirect(reverse_lazy("projects:project_detail", kwargs={"pk": new_obj.id}))


# STAFF #
#########

class StaffCreateView(CanModifyProjectRequiredMixin, CreateView):
    model = models.Staff
    template_name = 'projects/staff_form_popout.html'
    form_class = forms.StaffForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
            'funding_source': project.default_funding_source,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        context['help_text_dict'] = get_help_text_dict()
        return context

    def form_valid(self, form):
        object = form.save()
        if form.cleaned_data["save_then_go_OT"] == "1":
            return HttpResponseRedirect(reverse_lazy('projects:ot_calc', kwargs={"pk": object.id}))
        else:
            return HttpResponseRedirect(reverse('projects:close_me'))


class StaffUpdateView(CanModifyProjectRequiredMixin, UpdateView):
    model = models.Staff
    template_name = 'projects/staff_form_popout.html'
    form_class = forms.StaffForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()
        return context


def staff_delete(request, pk):
    object = models.Staff.objects.get(pk=pk)

    if can_modify_project(request.user, object.project.id):
        object.delete()
        messages.success(request, _("The staff member has been successfully deleted from project."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


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

        # send in the upcoming fiscal year string
        context["next_fiscal_year"] = fiscal_year(next=True)

        # create a pandas date_range object for upcoming fiscal year
        target_year = fiscal_year(next=True, sap_style=True)
        start = "{}-04-01".format(target_year - 1)
        end = "{}-03-31".format(target_year)
        datelist = pd.date_range(start=start, end=end).tolist()
        context['datelist'] = datelist

        # send in a list of stat holidays
        context["stat_holiday_list"] = stat_holidays.stat_holiday_list
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse_lazy('projects:staff_edit', kwargs={"pk": object.id}))


# this is a temp view DJF created to walkover the `program` field to the new `programs` field
@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def temp_formset(request, region, fy, section_str=None):
    context = {}
    # if the formset is being submitted
    if request.method == 'POST':
        # choose the appropriate formset based on the `extra` arg
        formset = forms.TempFormSet(request.POST)

        if formset.is_valid():
            formset.save()
            # pass the specimen through the make_flags helper function to assign any QC flags

            # redirect back to the observation_formset with the blind intention of getting another observation
            return HttpResponseRedirect(reverse("projects:formset", kwargs={"region": region, "fy": fy, "section_str": section_str}))
    # otherwise the formset is just being displayed
    else:
        # prep the formset...for display
        qs = models.Project.objects.filter(
            year=fy,
            section__division__branch__region__id=region,
            functional_group__isnull=True
        ).order_by("functional_group")

        if section_str:
            qs = qs.filter(section__name__icontains=section_str)

        formset = forms.TempFormSet(
            queryset=qs
        )
    context['formset'] = formset
    context['my_object'] = models.Project.objects.first()
    context['field_list'] = [
        "project_title",
        "section",
        "leads",
        "programs",
        "funding_sources",
        "activity_type",
        "default_funding_source",
        "functional_group",
    ]
    return render(request, 'projects/temp_formset.html', context)


# this is a temp view DJF created to walkover the `program` field to the new `programs` field
class MyTempListView(LoginRequiredMixin, ListView):
    queryset = models.Project.objects.filter(section__division__branch__region__id=2).order_by(
        "section__division__branch__region",
        "section__division",
        "section",
        "program",
    )
    template_name = 'projects/my_temp_list.html'


# COLLABORATOR #
################

class CollaboratorCreateView(CanModifyProjectRequiredMixin, CreateView):
    model = models.Collaborator
    template_name = 'projects/collaborator_form_popout.html'
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


class CollaboratorUpdateView(CanModifyProjectRequiredMixin, UpdateView):
    model = models.Collaborator
    template_name = 'projects/collaborator_form_popout.html'
    form_class = forms.CollaboratorForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def collaborator_delete(request, pk):
    object = models.Collaborator.objects.get(pk=pk)
    if can_modify_project(request.user, object.project.id):
        object.delete()
        messages.success(request, _("The collaborator has been successfully deleted from project."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


# AGREEMENTS #
##############

class AgreementCreateView(CanModifyProjectRequiredMixin, CreateView):
    model = models.CollaborativeAgreement
    template_name = 'projects/agreement_form_popout.html'
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


class AgreementUpdateView(CanModifyProjectRequiredMixin, UpdateView):
    model = models.CollaborativeAgreement
    template_name = 'projects/agreement_form_popout.html'
    form_class = forms.AgreementForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


def agreement_delete(request, pk):
    object = models.CollaborativeAgreement.objects.get(pk=pk)
    if can_modify_project(request.user, object.project.id):
        object.delete()
        messages.success(request, _("The agreement has been successfully deleted."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


# OM COSTS #
############

class OMCostCreateView(CanModifyProjectRequiredMixin, CreateView):
    model = models.OMCost
    template_name = 'projects/cost_form_popout.html'
    form_class = forms.OMCostForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
            'funding_source': project.default_funding_source,
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


class OMCostUpdateView(CanModifyProjectRequiredMixin, UpdateView):
    model = models.OMCost
    template_name = 'projects/cost_form_popout.html'
    form_class = forms.OMCostForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_type'] = _("O&M")
        return context


def om_cost_delete(request, pk):
    object = models.OMCost.objects.get(pk=pk)
    if can_modify_project(request.user, object.project.id):
        object.delete()
        messages.success(request, _("The cost has been successfully deleted."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


def om_cost_clear(request, project):
    project = models.Project.objects.get(pk=project)
    if can_modify_project(request.user, project.id):
        for obj in models.OMCategory.objects.all():
            for cost in models.OMCost.objects.filter(project=project, om_category=obj):
                print(cost)
                if (cost.budget_requested is None or cost.budget_requested == 0) and not cost.description:
                    cost.delete()

        messages.success(request, _("All empty O&M lines have been cleared."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


def om_cost_populate(request, project):
    project = models.Project.objects.get(pk=project)
    if can_modify_project(request.user, project.id):
        for obj in models.OMCategory.objects.all():
            if not models.OMCost.objects.filter(project=project, om_category=obj).count():
                new_item = models.OMCost.objects.create(project=project, om_category=obj)
                new_item.save()

        messages.success(request, _("All O&M categories have been added to this project."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


# CAPITAL COSTS #
#################

class CapitalCostCreateView(CanModifyProjectRequiredMixin, CreateView):
    model = models.CapitalCost
    template_name = 'projects/cost_form_popout.html'
    form_class = forms.CapitalCostForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
            'funding_source': project.default_funding_source,
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


class CapitalCostUpdateView(CanModifyProjectRequiredMixin, UpdateView):
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
    if can_modify_project(request.user, object.project.id):
        object.delete()
        messages.success(request, _("The cost has been successfully deleted."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


# GC COSTS #
############

class GCCostCreateView(CanModifyProjectRequiredMixin, CreateView):
    model = models.GCCost
    template_name = 'projects/cost_form_popout.html'
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


class GCCostUpdateView(CanModifyProjectRequiredMixin, UpdateView):
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
    if can_modify_project(request.user, object.project.id):
        object.delete()
        messages.success(request, _("The cost has been successfully deleted."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


# FILES #
#########

class FileCreateView(CanModifyProjectRequiredMixin, CreateView):
    template_name = "projects/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse("shared_models:close_me"))

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        project = models.Project.objects.get(pk=self.kwargs['project'])
        context["project"] = project
        return context

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        status_report = models.StatusReport.objects.get(pk=self.kwargs['status_report']) if self.kwargs.get('status_report') else None

        return {
            'project': project,
            'status_report': status_report,
        }


class FileUpdateView(CanModifyProjectRequiredMixin, UpdateView):
    template_name = "projects/file_form.html"
    model = models.File
    form_class = forms.FileForm

    def get_success_url(self, **kwargs):
        return reverse_lazy("projects:file_detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        # get context
        context = super().get_context_data(**kwargs)
        context["editable"] = True
        return context


class FileDetailView(FileUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["editable"] = False
        return context


class FileDeleteView(CanModifyProjectRequiredMixin, DeleteView):
    template_name = "projects/file_confirm_delete.html"
    model = models.File

    def get_success_url(self, **kwargs):
        return reverse_lazy("shared_models:close_me")


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
        my_user = User.objects.create(
            username=email,
            first_name=first_name,
            last_name=last_name,
            password="pbkdf2_sha256$120000$ctoBiOUIJMD1$DWVtEKBlDXXHKfy/0wKCpcIDYjRrKfV/wpYMHKVrasw=",
            is_active=1,
            email=email,
        )

        email = emails.UserCreationEmail(my_user)

        # send the email object
        if settings.PRODUCTION_SERVER:
            send_mail(message='', subject=email.subject, html_message=email.message, from_email=email.from_email,
                      recipient_list=email.to_list, fail_silently=False, )
        else:
            print(email)
        messages.success(self.request, _("The user was created and an email was sent"))

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# SETTINGS #
############

@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_funding_source(request, pk):
    my_obj = models.FundingSource.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_funding_sources"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_funding_sources(request):
    qs = models.FundingSource.objects.all()
    if request.method == 'POST':
        formset = forms.FundingSourceFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_funding_sources"))
    else:
        formset = forms.FundingSourceFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'color',
    ]
    context['title'] = "Manage Funding Sources"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_om_cat(request, pk):
    my_obj = models.OMCategory.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_om_cats"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_om_cats(request):
    qs = models.OMCategory.objects.all()
    if request.method == 'POST':
        formset = forms.OMCategoryFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_om_cats"))
    else:
        formset = forms.OMCategoryFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'group',
    ]
    context['title'] = "Manage O & M Categories"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_employee_type(request, pk):
    my_obj = models.EmployeeType.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_employee_types"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_employee_types(request):
    qs = models.EmployeeType.objects.all()
    if request.method == 'POST':
        formset = forms.EmployeeTypeFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_employee_types"))
    else:
        formset = forms.EmployeeTypeFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'cost_type',
        'exclude_from_rollup',
    ]
    context['title'] = "Manage Employee Types"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_status(request, pk):
    my_obj = models.Status.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_statuses"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_statuses(request):
    qs = models.Status.objects.all()
    if request.method == 'POST':
        formset = forms.StatusFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_statuses"))
    else:
        formset = forms.StatusFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'used_for',
        'name',
        'nom',
        'order',
        'color',
    ]
    context['title'] = "Manage Statuses"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_tag(request, pk):
    my_obj = models.Tag.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_tags"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_tags(request):
    qs = models.Tag.objects.all()
    if request.method == 'POST':
        formset = forms.TagFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_tags"))
    else:
        formset = forms.TagFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
    ]
    context['title'] = "Manage Tags"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_help_text(request, pk):
    my_obj = models.HelpText.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_help_text"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_help_text(request):
    qs = models.HelpText.objects.all()
    if request.method == 'POST':
        formset = forms.HelpTextFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_help_text"))
    else:
        formset = forms.HelpTextFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'field_name',
        'eng_text',
        'fra_text',
    ]
    context['title'] = "Manage Help Text"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_level(request, pk):
    my_obj = models.Level.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_levels"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_levels(request):
    qs = models.Level.objects.all()
    if request.method == 'POST':
        formset = forms.LevelFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_levels"))
    else:
        formset = forms.LevelFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
    ]
    context['title'] = "Manage Levels"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_program(request, pk):
    my_obj = models.Program.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_programs"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_programs(request):
    qs = models.Program.objects.all().order_by("regional_program_name_eng")
    if request.method == 'POST':
        formset = forms.ProgramFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_programs"))
    else:
        formset = forms.ProgramFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'national_responsibility_eng|National responsibility',
        'program_inventory',
        'funding_source_and_type',
        'regional_program_name_eng|Regional program name',
        'short_name',
        'is_core',
        'examples',
        'theme',
    ]
    context['title'] = "Manage Programs"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_functional_group(request, pk):
    my_obj = models.FunctionalGroup.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_functional_groups"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_functional_groups(request):
    qs = models.FunctionalGroup.objects.all()
    if request.method == 'POST':
        formset = forms.FunctionalGroupFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_functional_groups"))
    else:
        formset = forms.FunctionalGroupFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
        'program',
        'sections',
    ]
    context['title'] = "Manage Functional Groups"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def delete_theme(request, pk):
    my_obj = models.Theme.objects.get(pk=pk)
    my_obj.delete()
    return HttpResponseRedirect(reverse("projects:manage_functional_groups"))


@login_required(login_url='/accounts/login_required/')
@user_passes_test(in_projects_admin_group, login_url='/accounts/denied/')
def manage_themes(request):
    qs = models.Theme.objects.all()
    if request.method == 'POST':
        formset = forms.ThemeFormSet(request.POST, )
        if formset.is_valid():
            formset.save()
            # do something with the formset.cleaned_data
            messages.success(request, "Items have been successfully updated")
            return HttpResponseRedirect(reverse("projects:manage_themes"))
    else:
        formset = forms.ThemeFormSet(
            queryset=qs)
    context = {}
    context["my_object"] = qs.first()
    context["field_list"] = [
        'name',
        'nom',
    ]
    context['title'] = "Manage Themes"
    context['formset'] = formset
    return render(request, 'projects/manage_settings_small.html', context)


class AdminStaffListView(ManagerOrAdminRequiredMixin, FilterView):
    template_name = 'projects/admin_staff_list.html'
    queryset = models.Staff.objects.filter(user__isnull=True).order_by('-project__year', 'project__section__division', 'project__section',
                                                                       'project__project_title')
    filterset_class = filters.StaffFilter


class AdminStaffUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
    '''This is really just for the admin view'''
    model = models.Staff
    template_name = 'projects/admin_staff_form.html'
    form_class = forms.AdminStaffForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse("projects:admin_staff_list") + "?" + nz(self.kwargs.get("qry"), ""))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()
        return context


class AdminProjectProgramListView(ManagerOrAdminRequiredMixin, FilterView):
    template_name = 'projects/admin_project_program_list.html'
    queryset = models.Project.objects.all().order_by('-year', 'id')
    filterset_class = filters.AdminProjectProgramFilter


class AdminProjectProgramUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
    '''This is really just for the admin view'''
    model = models.Project
    template_name = 'projects/admin_project_program_form.html'
    form_class = forms.AdminProjectProgramForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse("projects:admin_project_program_list") + "?" + nz(self.kwargs.get("qry"), ""))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()
        return context


class SubmittedUnapprovedProjectsListView(ManagerOrAdminRequiredMixin, FilterView):
    template_name = 'projects/admin_submitted_unapproved_list.html'
    queryset = models.Project.objects.filter(submitted=True, approved=False).order_by('-year', 'id')
    filterset_class = filters.AdminSubmittedUnapprovedFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_qs = context.get("filter").qs
        # models.Project.objects.values("section").
        my_qs = my_qs.values("year_id", "section_id").order_by("year_id", "section_id").distinct().annotate(dcount=Count("id"))

        section_dict = {}
        for s in shared_models.Section.objects.all():
            section_dict[s.id] = s

        fy_dict = {}
        for fy in shared_models.FiscalYear.objects.all():
            fy_dict[fy.id] = fy

        section_year_program_dict = {}
        for fy in shared_models.FiscalYear.objects.all():
            if fy.projects.filter(submitted=True, approved=True).count() > 0:
                section_year_program_dict[fy.id] = {}
                for s in shared_models.Section.objects.all():
                    if s.projects.filter(submitted=True, approved=True).count() > 0:
                        section_year_program_dict[fy.id][s.id] = {}
                        project_list = context.get("filter").qs.filter(year=fy, section=s)
                        # section_year_program_dict[fy.id][s.id]["programs"] = \
                        #     models.Program.objects.filter(projects__in=project_list).distinct()

                        # determine if there are submitted project with no programs
                        # section_year_program_dict[fy.id][s.id]["program_errors"] = project_list.filter(programs__isnull=True)
                        section_year_program_dict[fy.id][s.id]["project_list"] = project_list.order_by("programs__is_core").distinct()

        context["my_qs"] = my_qs
        context["section_dict"] = section_dict
        context["fy_dict"] = fy_dict
        context["section_year_program_dict"] = section_year_program_dict
        return context


# STATUS REPORT #
#################

class StatusReportCreateView(ProjectLeadRequiredMixin, CreateView):
    model = models.StatusReport
    template_name = 'projects/status_report_form_popout.html'
    form_class = forms.StatusReportForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
            'created_by': self.request.user,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        context['status_report'] = True
        context['files'] = project.files.all()
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy('projects:report_edit', kwargs={"pk": my_object.id}))


class StatusReportUpdateView(ProjectLeadRequiredMixin, UpdateView):
    model = models.StatusReport
    template_name = 'projects/status_report_form_popout.html'

    # form_class = forms.StatusReportForm

    def get_form_class(self):
        my_project = self.get_object().project
        if is_section_head(self.request.user, my_project):
            return forms.StatusReportSectionHeadForm
        else:
            return forms.StatusReportForm

    def get_initial(self):
        return {'created_by': self.request.user, }

    def dispatch(self, request, *args, **kwargs):
        # when the view loads, let's make sure that all the milestones are on the project.
        my_object = self.get_object()
        my_project = my_object.project
        for milestone in my_project.milestones.all():
            my_update, created = models.MilestoneUpdate.objects.get_or_create(
                milestone=milestone,
                status_report=my_object
            )
            # if the update is being created, what should be the starting status?
            # to know, we would have to look and see if there is another report. if there is, we should grab the penultimate report and copy status from there.
            if created:
                # check to see if there is another update on the same milestone. We can do this since milestones are unique to projects.
                if milestone.updates.count() > 1:
                    # if there are more than just 1 (i.e. the one we just created), it will be the second record we are interested in...
                    last_update = milestone.updates.all()[1]
                    my_update.status = last_update.status
                    my_update.save()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = context["object"].project
        context['status_report'] = self.get_object()
        context['project'] = project
        context['files'] = self.get_object().files.all()
        context["can_edit"] = can_modify_project(self.request.user, project.id)
        context["is_lead"] = self.request.user in [staff.user for staff in project.staff_members.filter(lead=True)]
        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse_lazy('projects:report_edit', kwargs={"pk": my_object.id}))


class StatusReportDeleteView(CanModifyProjectRequiredMixin, DeleteView):
    template_name = "projects/status_report_confirm_delete.html"
    model = models.StatusReport

    def get_success_url(self, **kwargs):
        return reverse_lazy("shared_models:close_me")


class StatusReportPrintDetailView(LoginRequiredMixin, PDFTemplateView):
    model = models.Project
    login_url = '/accounts/login_required/'
    template_name = "projects/status_report_pdf.html"

    def get_pdf_filename(self):
        my_report = models.StatusReport.objects.get(pk=self.kwargs["pk"])
        pdf_filename = "{}.pdf".format(
            my_report
        )
        return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_report = models.StatusReport.objects.get(pk=self.kwargs["pk"])
        context["object"] = my_report
        context["report_mode"] = True
        context['files'] = my_report.files.all()

        context["field_list"] = [
            'date_created',
            'created_by',
            'status',
            'major_accomplishments',
            'major_issues',
            'target_completion_date',
            'rationale_for_modified_completion_date',
            'general_comment',
            'section_head_comment',
            'section_head_reviewed',
        ]

        return context


# MILESTONE #
#############

class MilestoneCreateView(ProjectLeadRequiredMixin, CreateView):
    model = models.Milestone
    template_name = 'projects/milestone_form_popout.html'
    form_class = forms.MilestoneForm

    def get_initial(self):
        project = models.Project.objects.get(pk=self.kwargs['project'])
        return {
            'project': project,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = models.Project.objects.get(id=self.kwargs['project'])
        context['project'] = project
        # context['cost_type'] = "G&C"
        return context

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))


class MilestoneUpdateView(ProjectLeadRequiredMixin, UpdateView):
    model = models.Milestone
    template_name = 'projects/milestone_form_popout.html'
    form_class = forms.MilestoneForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = context["object"].project
        return context


def milestone_delete(request, pk):
    object = models.Milestone.objects.get(pk=pk)
    if can_modify_project(request.user, object.project.id):
        object.delete()
        messages.success(request, _("The milestone has been successfully deleted."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return HttpResponseRedirect(reverse('accounts:denied_project_leads_only'))


# MILESTONE UPDATE #
####################

class MilestoneUpdateUpdateView(UpdateView):
    model = models.MilestoneUpdate
    template_name = 'projects/milestone_form_popout.html'
    form_class = forms.MilestoneUpdateForm

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse('projects:close_me'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['project'] = context["object"].project
        return context


# REPORTS #
###########

class ReportSearchFormView(ManagerOrAdminRequiredMixin, FormView):
    template_name = 'projects/report_search.html'
    form_class = forms.ReportSearchForm

    def get_initial(self):
        # default the year to the year of the latest samples
        return {"fiscal_year": fiscal_year(next=True, sap_style=True)}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        division_dict = {}
        for d in get_division_choices():
            my_division = shared_models.Division.objects.get(pk=d[0])
            division_dict[my_division.id] = {}
            division_dict[my_division.id]["display"] = getattr(my_division, _("name"))
            division_dict[my_division.id]["region_id"] = my_division.branch.region_id

        section_dict = {}
        for s in get_section_choices():
            my_section = shared_models.Section.objects.get(pk=s[0])
            section_dict[my_section.id] = {}
            section_dict[my_section.id]["display"] = str(my_section)
            section_dict[my_section.id]["division_id"] = my_section.division_id

        context['division_json'] = json.dumps(division_dict)
        context['section_json'] = json.dumps(section_dict)
        return context

    def form_valid(self, form):
        fiscal_year = str(form.cleaned_data["fiscal_year"])
        report = int(form.cleaned_data["report"])
        regions = listrify(form.cleaned_data["region"])
        divisions = listrify(form.cleaned_data["division"])
        sections = listrify(form.cleaned_data["section"])

        if regions == "":
            regions = "None"
        if divisions == "":
            divisions = "None"
        if sections == "":
            sections = "None"

        if report == 1:
            return HttpResponseRedirect(reverse("projects:report_master", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 2:
            return HttpResponseRedirect(reverse("projects:pdf_printout", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 3:
            return HttpResponseRedirect(reverse("projects:pdf_project_summary", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 4:
            return HttpResponseRedirect(reverse("projects:export_program_list", kwargs={}))

        elif report == 10:
            return HttpResponseRedirect(reverse("projects:pdf_fte_summary", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 11:
            return HttpResponseRedirect(reverse("projects:pdf_ot", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 12:
            return HttpResponseRedirect(reverse("projects:pdf_costs", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 13:
            return HttpResponseRedirect(reverse("projects:pdf_collab", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 15:
            return HttpResponseRedirect(reverse("projects:pdf_agreements", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 14:
            return HttpResponseRedirect(reverse("projects:doug_report", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 16:
            return HttpResponseRedirect(reverse("projects:pdf_feedback", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        elif report == 17:
            return HttpResponseRedirect(reverse("projects:pdf_data", kwargs={
                'fiscal_year': fiscal_year,
                'regions': regions,
                'divisions': divisions,
                'sections': sections,
            }))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("projects:report_search"))


def master_spreadsheet(request, fiscal_year, regions=None, divisions=None, sections=None, user=None):
    # sections arg will be coming in as None from the my_section view
    if regions is None:
        regions = "None"
    if divisions is None:
        divisions = "None"
    if sections is None:
        sections = "None"

    file_url = reports.generate_master_spreadsheet(fiscal_year, regions, divisions, sections, user)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="Science project planning MASTER LIST {}.xlsx"'.format(
                fiscal_year)
            return response
    raise Http404


def dougs_spreadsheet(request, fiscal_year, regions=None, divisions=None, sections=None):
    # sections arg will be coming in as None from the my_section view
    if regions is None:
        regions = "None"
    if divisions is None:
        divisions = "None"
    if sections is None:
        sections = "None"

    file_url = reports.generate_dougs_spreadsheet(fiscal_year, regions, divisions, sections)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="Dougs Spreadsheet {}.xlsx"'.format(
                fiscal_year)
            return response
    raise Http404


class PDFProjectSummaryReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_project_summary.html"

    def get_pdf_filename(self):
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
        pdf_filename = "{} Project Summary Report.pdf".format(fy)
        return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            section_list = shared_models.Section.objects.filter(division_id__in=self.kwargs["divisions"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            section_list = shared_models.Section.objects.filter(division__branch__region_id__in=self.kwargs["regions"].split(","))
        else:
            section_list = []

        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id")

        context["fy"] = fy
        context["report_mode"] = True
        context["object_list"] = project_list
        context["field_list"] = project_field_list
        context["division_list"] = [shared_models.Division.objects.get(pk=item["section__division"]) for item in
                                    project_list.values("section__division").order_by("section__division").distinct()]
        # bring in financial summary data for each project:
        context["financial_summary_data"] = {}
        context["financial_summary_data"]["sections"] = {}
        context["financial_summary_data"]["divisions"] = {}
        key_list = [
            "salary_abase",
            "salary_bbase",
            "salary_cbase",
            "om_abase",
            "om_bbase",
            "om_cbase",
            "capital_abase",
            "capital_bbase",
            "capital_cbase",
            "salary_total",
            "om_total",
            "capital_total",
            "students",
            "casuals",
            "OT",
        ]

        for project in project_list:
            context["financial_summary_data"][project.id] = financial_summary_data(project)
            context["financial_summary_data"][project.id]["students"] = project.staff_members.filter(employee_type=4).count()
            context["financial_summary_data"][project.id]["casuals"] = project.staff_members.filter(employee_type=3).count()
            context["financial_summary_data"][project.id]["OT"] = nz(project.staff_members.values("overtime_hours").order_by(
                "overtime_hours").aggregate(dsum=Sum("overtime_hours"))["dsum"], 0)

            # for sections
            try:
                context["financial_summary_data"]["sections"][project.section.id]
            except KeyError:
                context["financial_summary_data"]["sections"][project.section.id] = {}
                # go through the keys and make sure each category is initialized
                for key in key_list:
                    context["financial_summary_data"]["sections"][project.section.id][key] = 0
            finally:
                for key in key_list:
                    context["financial_summary_data"]["sections"][project.section.id][key] += context["financial_summary_data"][project.id][
                        key]

            # for Divisions
            try:
                context["financial_summary_data"]["divisions"][project.section.division.id]
            except KeyError:
                context["financial_summary_data"]["divisions"][project.section.division.id] = {}
                # go through the keys and make sure each category is initialized
                for key in key_list:
                    context["financial_summary_data"]["divisions"][project.section.division.id][key] = 0
            finally:
                for key in key_list:
                    context["financial_summary_data"]["divisions"][project.section.division.id][key] += \
                        context["financial_summary_data"][project.id][key]

            # for total
            try:
                context["financial_summary_data"]["total"]
            except KeyError:
                context["financial_summary_data"]["total"] = {}
                # go through the keys and make sure each category is initialized
                for key in key_list:
                    context["financial_summary_data"]["total"][key] = 0
            finally:
                for key in key_list:
                    context["financial_summary_data"]["total"][key] += \
                        context["financial_summary_data"][project.id][key]

        # get a list of the capital requests
        context["capital_list"] = [capital_cost for project in project_list for capital_cost in project.capital_costs.all()]

        # get a list of the G&Cs
        context["gc_list"] = [gc for project in project_list for gc in project.gc_costs.all()]

        # get a list of the collaborators
        context["collaborator_list"] = [collaborator for project in project_list for collaborator in project.collaborators.all()]

        # get a list of the agreements
        context["agreement_list"] = [agreement for project in project_list for agreement in project.agreements.all()]

        return context


class PDFProjectPrintoutReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_printout.html"

    def get_pdf_filename(self):
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
        pdf_filename = "{} Workplan Export.pdf".format(fy)
        return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            section_list = shared_models.Section.objects.filter(division_id__in=self.kwargs["divisions"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            section_list = shared_models.Section.objects.filter(division__branch__region_id__in=self.kwargs["regions"].split(","))
        else:
            section_list = []

        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id")

        # project_list = [project for project in project_list if project.section in section_list]

        context["fy"] = fy
        context["report_mode"] = True
        context["object_list"] = project_list
        context["field_list"] = project_field_list
        context["division_list"] = set([s.division for s in section_list])
        # bring in financial summary data for each project:
        context["financial_summary_data"] = {}
        context["financial_summary_data"]["sections"] = {}
        context["financial_summary_data"]["divisions"] = {}
        key_list = [
            "salary_abase",
            "salary_bbase",
            "salary_cbase",
            "om_abase",
            "om_bbase",
            "om_cbase",
            "capital_abase",
            "capital_bbase",
            "capital_cbase",
            "students",
            "casuals",
            "OT",
        ]

        for project in project_list:
            context["financial_summary_data"][project.id] = financial_summary_data(project)

        return context


def workplan_summary(request, fiscal_year):
    file_url = reports.generate_workplan_summary(fiscal_year)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="{} Workplan Summary.xlsx"'.format(
                fiscal_year)
            return response
    raise Http404


def export_program_list(request):
    file_url = reports.generate_program_list()

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="Science Program List.xlsx"'
            return response
    raise Http404


class PDFCollaboratorReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_collaborators.html"

    # def get_pdf_filename(self):
    #     fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
    #     pdf_filename = "{} Project Summary Report.pdf".format(fy)
    #     return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            section_list = shared_models.Section.objects.filter(division_id__in=self.kwargs["divisions"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            section_list = shared_models.Section.objects.filter(division__branch__region_id__in=self.kwargs["regions"].split(","))
        else:
            section_list = []

        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id")

        collaborator_list = models.Collaborator.objects.filter(project__in=project_list)

        context["fy"] = fy
        context["object_list"] = collaborator_list
        context["my_object"] = collaborator_list.first()
        context["field_list"] = [
            'name',
            'critical',
            'notes',
            'project',
        ]

        return context


class PDFAgreementsReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_agreements.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            section_list = shared_models.Section.objects.filter(division_id__in=self.kwargs["divisions"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            section_list = shared_models.Section.objects.filter(division__branch__region_id__in=self.kwargs["regions"].split(","))
        else:
            section_list = []

        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id")
        collaborator_list = models.CollaborativeAgreement.objects.filter(project__in=project_list)

        context["fy"] = fy
        context["object_list"] = collaborator_list
        context["my_object"] = collaborator_list.first()
        context["field_list"] = [
            'agreement_title',
            'partner_organization',
            'project_lead',
            'new_or_existing',
            'project',
            'notes',
        ]
        return context


class PDFFeedbackReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_feedback.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            section_list = shared_models.Section.objects.filter(division_id__in=self.kwargs["divisions"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            section_list = shared_models.Section.objects.filter(division__branch__region_id__in=self.kwargs["regions"].split(","))
        else:
            section_list = []

        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id").filter(~Q(feedback=""))
        context["fy"] = fy
        context["object_list"] = project_list
        context["my_object"] = project_list.first()
        context["field_list"] = [
            'id',
            'project_title',
            'project_leads|Project leads',
            'feedback',
        ]

        return context


class PDFDataReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_data.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            section_list = shared_models.Section.objects.filter(division_id__in=self.kwargs["divisions"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            section_list = shared_models.Section.objects.filter(division__branch__region_id__in=self.kwargs["regions"].split(","))
        else:
            section_list = []

        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id")
        context["fy"] = fy
        context["object_list"] = project_list
        context["my_object"] = project_list.first()
        context["field_list"] = [
            'id',
            'project_title',
            'project_leads|Project leads',
            'data_collection',
            'data_sharing',
            'data_storage',
            'metadata_url',
            'regional_dm_needs',
            'sectional_dm_needs',
        ]

        return context


class PDFFTESummaryReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_fte_summary.html"

    # def get_pdf_filename(self):
    #     fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
    #     pdf_filename = "{} Project Summary Report.pdf".format(fy)
    #     return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            section_list = shared_models.Section.objects.filter(division_id__in=self.kwargs["divisions"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            section_list = shared_models.Section.objects.filter(division__branch__region_id__in=self.kwargs["regions"].split(","))
        else:
            section_list = []

        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id")

        staff_list = models.Staff.objects.filter(
            project__in=project_list,
            # employee_type_id__in=[1,]
            user__isnull=False
        ).order_by("user__last_name", "user__first_name").values("user").annotate(dsum=Sum("duration_weeks"))

        # users = [models.Staff.objects.get(pk=item["user"]) for item in staff_list]
        # hours = [item["dsum"] for item in staff_list]

        context["fy"] = fy
        # context["users"] = users
        my_dict = {}
        for i in range(0, len(staff_list)):
            my_dict[i] = {}
            my_dict[i]["user"] = User.objects.get(pk=staff_list[i]["user"])
            my_dict[i]["hours"] = staff_list[i]["dsum"]
        context["my_dict"] = my_dict

        non_reg_staff_list = models.Staff.objects.filter(user__isnull=True).order_by("name")
        context["non_reg_staff_list"] = non_reg_staff_list

        return context


class PDFOTSummaryReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_ot_summary.html"

    # def get_pdf_filename(self):
    #     fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
    #     pdf_filename = "{} Project Summary Report.pdf".format(fy)
    #     return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
            division_list = shared_models.Division.objects.filter(id__in=[section.division.id for section in section_list])
            # region_list = shared_models.Region.objects.filter(id__in=[division.region.id for division in division_list])
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            division_list = shared_models.Division.objects.filter(id__in=self.kwargs["divisions"].split(","))
            section_list = shared_models.Section.objects.filter(division__in=division_list)
            # region_list = shared_models.Region.objects.filter(id__in=[division.region.id for division in division_list])
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            region_list = shared_models.Region.objects.filter(id__in=self.kwargs["regions"].split(","))
            division_list = shared_models.Division.objects.filter(branch__region__in=region_list, branch__id__in=[1, 3])
            section_list = shared_models.Section.objects.filter(division__in=division_list)
        else:
            section_list = []
            division_list = []
            # region_list = []

        # there will always be a section list so let's use that to generate a project list
        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id")
        context["fy"] = fy

        # NOTE this report is not meant to contain multiple regions...
        context["division_list"] = division_list
        context["section_list"] = section_list

        # bring in financial summary data for each project:
        my_dict = {}
        my_dict["total"] = 0
        my_dict["programs"] = {}
        for division in division_list:
            # create a sub dict for the division
            my_dict[division] = {}
            my_dict[division]["total"] = 0
            my_dict[division]["nrows"] = 0

            for section in division.sections.all():
                # exclude any sections that are not in the section list
                if section in section_list:
                    # create a sub sub dict for the section
                    project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True, section=section)

                    ot = models.Staff.objects.filter(
                        project__in=project_list, overtime_hours__isnull=False,
                    ).aggregate(dsum=Sum("overtime_hours"))["dsum"]
                    my_dict[division][section] = {}
                    my_dict[division][section]["total"] = ot
                    my_dict[division]["total"] += nz(ot, 0)
                    my_dict["total"] += nz(ot, 0)

                    # now get the progam list for all the section
                    program_list = models.Program.objects.filter(projects__in=project_list).distinct()
                    my_dict[division]["nrows"] += program_list.count()
                    my_dict[division][section]["programs"] = {}
                    my_dict[division][section]["programs"]["list"] = program_list
                    for program in program_list:
                        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True, section=section,
                                                                     programs=program)

                        ot = models.Staff.objects.filter(
                            project__in=project_list, overtime_hours__isnull=False,
                        ).aggregate(dsum=Sum("overtime_hours"))["dsum"]

                        my_dict[division][section]["programs"][program] = ot

                        if not my_dict["programs"].get(program):
                            my_dict["programs"][program] = 0

                        my_dict["programs"][program] += nz(ot, 0)

        program_list = models.Program.objects.filter(id__in=[program.id for program in my_dict["programs"]]).distinct()
        my_dict["programs"]["list"] = program_list

        context["ot_summary_data"] = my_dict

        return context


class PDFCostSummaryReport(LoginRequiredMixin, PDFTemplateView):
    login_url = '/accounts/login_required/'
    template_name = "projects/report_pdf_cost_summary.html"

    # def get_pdf_filename(self):
    #     fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
    #     pdf_filename = "{} Project Summary Report.pdf".format(fy)
    #     return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])

        # need to assemble a section list
        ## first look at the sections arg; if not null, we don't need anything else
        if self.kwargs["sections"] != "None":
            section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["divisions"] != "None":
            section_list = shared_models.Section.objects.filter(division_id__in=self.kwargs["divisions"].split(","))
        ## next look at the divisions arg; if not null, we don't need anything else
        elif self.kwargs["regions"] != "None":
            section_list = shared_models.Section.objects.filter(division__branch__region_id__in=self.kwargs["regions"].split(","))
        else:
            section_list = []

        project_list = models.Project.objects.filter(year=fy, submitted=True, approved=True,
                                                     section_id__in=section_list).order_by("id")

        context["fy"] = fy
        context["object_list"] = project_list
        context["division_list"] = [shared_models.Division.objects.get(pk=item["section__division"]) for item in
                                    project_list.values("section__division").order_by("section__division").distinct()]
        # bring in financial summary data for each project:
        context["financial_summary_data"] = {}
        context["financial_summary_data"]["sections"] = {}
        context["financial_summary_data"]["divisions"] = {}
        key_list = [
            "salary_abase",
            "salary_bbase",
            "salary_cbase",
            "om_abase",
            "om_bbase",
            "om_cbase",
            "capital_abase",
            "capital_bbase",
            "capital_cbase",
            "salary_total",
            "om_total",
            "capital_total",
            "students",
            "casuals",
        ]

        for project in project_list:
            context["financial_summary_data"][project.id] = financial_summary_data(project)
            context["financial_summary_data"][project.id]["students"] = project.staff_members.filter(employee_type=4).count()
            context["financial_summary_data"][project.id]["casuals"] = project.staff_members.filter(employee_type=3).count()

            # for sections
            try:
                context["financial_summary_data"]["sections"][project.section.id]
            except KeyError:
                context["financial_summary_data"]["sections"][project.section.id] = {}
                # go through the keys and make sure each category is initialized
                for key in key_list:
                    context["financial_summary_data"]["sections"][project.section.id][key] = 0
            finally:
                for key in key_list:
                    context["financial_summary_data"]["sections"][project.section.id][key] += context["financial_summary_data"][project.id][
                        key]

            # for Divisions
            try:
                context["financial_summary_data"]["divisions"][project.section.division.id]
            except KeyError:
                context["financial_summary_data"]["divisions"][project.section.division.id] = {}
                # go through the keys and make sure each category is initialized
                for key in key_list:
                    context["financial_summary_data"]["divisions"][project.section.division.id][key] = 0
            finally:
                for key in key_list:
                    context["financial_summary_data"]["divisions"][project.section.division.id][key] += \
                        context["financial_summary_data"][project.id][key]

            # for total
            try:
                context["financial_summary_data"]["total"]
            except KeyError:
                context["financial_summary_data"]["total"] = {}
                # go through the keys and make sure each category is initialized
                for key in key_list:
                    context["financial_summary_data"]["total"][key] = 0
            finally:
                for key in key_list:
                    context["financial_summary_data"]["total"][key] += \
                        context["financial_summary_data"][project.id][key]

        context["abase"] = models.FundingSource.objects.get(pk=1).color
        context["bbase"] = models.FundingSource.objects.get(pk=2).color
        context["cbase"] = models.FundingSource.objects.get(pk=3).color
        return context


# EXTRAS #
##########
class IWGroupList(ManagerOrAdminRequiredMixin, TemplateView):
    template_name = 'projects/iw_group_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fy = shared_models.FiscalYear.objects.get(id=self.kwargs.get("fiscal_year"))
        context['fy'] = fy
        my_region = shared_models.Region.objects.get(pk=self.kwargs.get("region"))
        context['region'] = my_region

        project_list = models.Project.objects.filter(
            section__division__branch__region=my_region,
            year=fy,
            submitted=True,
        )
        # If GULF region, we will further refine the list of projects
        if my_region.id == 1:
            project_list = models.Project.objects.filter(approved=True)

        division_list = shared_models.Division.objects.filter(sections__projects__in=project_list).distinct().order_by()
        section_list = shared_models.Section.objects.filter(projects__in=project_list).distinct().order_by()

        my_dict = {}
        for d in division_list.order_by("name"):
            my_dict[d] = {}
            for s in section_list.order_by("division", "name"):
                if s.division == d:
                    my_dict[d][s] = {}

                    # for each section, get a list of projects..  then programs
                    project_list = s.projects.filter(year=fy, submitted=True)
                    if my_region.id == 1:
                        project_list = project_list.filter(approved=True)

                    group_list = set([project.functional_group for project in project_list])

                    my_dict[d][s]["projects"] = project_list
                    my_dict[d][s]["groups"] = {}
                    for group in group_list:
                        my_dict[d][s]["groups"][group] = {}

                        # get a list of project counts
                        project_count = project_list.filter(functional_group=group).count()
                        my_dict[d][s]["groups"][group]["project_count"] = project_count

                        # get a list of project leads
                        leads = listrify(
                            list(set([str(staff.user) for staff in
                                      models.Staff.objects.filter(project__in=project_list.filter(functional_group=group), lead=True) if
                                      staff.user])))
                        my_dict[d][s]["groups"][group]["leads"] = leads
        context['my_dict'] = my_dict
        return context


class IWProjectList(ManagerOrAdminRequiredMixin, TemplateView):
    template_name = 'projects/iw_project_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fy = shared_models.FiscalYear.objects.get(id=self.kwargs.get("fiscal_year"))
        section = shared_models.Section.objects.get(id=self.kwargs.get("section"))
        functional_group = models.FunctionalGroup.objects.get(id=self.kwargs.get("group")) if self.kwargs.get("group") else None
        context['fy'] = fy
        context['section'] = section
        context['functional_group'] = functional_group

        project_list = models.Project.objects.filter(
            year=fy,
            section=section,
            submitted=True,
        ).order_by("id")

        # If from gulf region, filter out any un approved projects
        if section.division.branch.region.id == 1:
            project_list = project_list.filter(
                approved=True,
            )

        # If a function group is provided keep only those projects
        if self.kwargs.get("group"):
            project_list = project_list.filter(functional_group=functional_group, )

        context['project_list'] = project_list
        context["field_list"] = [
            "id|{}".format(_("Project Id")),
            "project_title",
            "functional_group",
            "activity_type",
            "default_funding_source",
            "tags",
            "project_leads|{}".format(_("Project leads")),
            "total_fte|{}".format(_("Total FTE")),
            "total_ot|{}".format(_("Total OT")),
            "meeting_notes",
        ]

        context["financials_dict"] = multiple_projects_financial_summary(project_list)

        return context


# FUNCTIONAL GROUPS #
#####################

class FunctionalGroupListView(AdminRequiredMixin, ListView):
    model = models.FunctionalGroup
    template_name = 'projects/functionalgroup_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["field_list"] = [
            'name',
            'nom',
            'program',
            'sections',
        ]
        return context

class FunctionalGroupUpdateView(AdminRequiredMixin, UpdateView):
    model = models.FunctionalGroup
    form_class = forms.FunctionalGroupForm
    success_url = reverse_lazy('projects:group_list')
    template_name = 'projects/functionalgroup_form.html'


class FunctionalGroupCreateView(AdminRequiredMixin, CreateView):
    model = models.FunctionalGroup
    form_class = forms.FunctionalGroupForm
    success_url = reverse_lazy('projects:group_list')
    template_name = 'projects/functionalgroup_form.html'


class FunctionalGroupDeleteView(AdminRequiredMixin, DeleteView):
    model = models.FunctionalGroup
    success_url = reverse_lazy('projects:group_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'projects/functionalgroup_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class FunctionalGroupDetailView(AdminRequiredMixin, DetailView):
    model = models.FunctionalGroup
    template_name = 'projects/functionalgroup_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'code',
            'name',
            'allotment_category',
        ]
        return context
