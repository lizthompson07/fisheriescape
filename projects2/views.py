import json
from copy import deepcopy

import pandas as pd
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy
from django.views.generic import UpdateView, CreateView
from easy_pdf.views import PDFTemplateView

from dm_apps.utils import custom_send_mail
from lib.functions.custom_functions import fiscal_year
from shared_models import models as shared_models
from shared_models.views import CommonTemplateView, CommonCreateView, \
    CommonDetailView, CommonFilterView, CommonDeleteView, CommonUpdateView, CommonListView, CommonHardDeleteView, CommonFormsetView
from . import emails
from . import filters
from . import forms
from . import models
from . import stat_holidays
from .mixins import CanModifyProjectRequiredMixin, ProjectLeadRequiredMixin, ManagerOrAdminRequiredMixin, AdminRequiredMixin
from .utils import multiple_projects_financial_summary, financial_summary_data, can_modify_project, get_help_text_dict, \
    get_division_choices, get_section_choices, get_project_field_list, get_project_year_field_list, is_management_or_admin


class IndexTemplateView(LoginRequiredMixin, CommonTemplateView):
    template_name = 'projects2/index.html'
    h1 = gettext_lazy("DFO Science Project Planning")
    active_page_name_crumb = gettext_lazy("Home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_id_list = []
        if self.request.user.id:
            if self.request.user.groups.filter(name="projects_admin").count() > 0:
                section_id_list = [project.section_id for project in models.Project.objects.all()]
                section_list = shared_models.Section.objects.filter(id__in=section_id_list)
            else:
                pass
                # # are they section heads?
                # section_id_list.extend([section.id for section in self.request.user.shared_models_sections.all()])
                #
                # # are they a division manager?
                # if self.request.user.shared_models_divisions.count() > 0:
                #     for division in self.request.user.shared_models_divisions.all():
                #         for section in division.sections.all():
                #             section_id_list.append(section.id)
                #
                # # are they an RDS?
                # if self.request.user.shared_models_branches.count() > 0:
                #     for branch in self.request.user.shared_models_branches.all():
                #         for division in branch.divisions.all():
                #             for section in division.sections.all():
                #                 section_id_list.append(section.id)
                #
                # section_id_set = set(
                #     [s for s in section_id_list if shared_models.Section.objects.get(pk=s).projects.count() > 0])
                # section_list = shared_models.Section.objects.filter(id__in=section_id_set)
            # context["section_list"] = section_list
        context["is_management_or_admin"] = is_management_or_admin(self.request.user)
        context["reference_materials"] = models.ReferenceMaterial.objects.all()
        context["upcoming_dates"] = models.UpcomingDate.objects.filter(date__gte=timezone.now()).order_by("date")
        context["past_dates"] = models.UpcomingDate.objects.filter(date__lt=timezone.now()).order_by("date")
        context["upcoming_dates_field_list"] = [
            "date",
            "region",
            "tdescription|{}".format("description"),
        ]
        return context


# PROJECTS #
############

class ProjectListView(ManagerOrAdminRequiredMixin, CommonFilterView):
    template_name = 'projects2/list.html'
    paginate_by = 15
    # get all submitted and unhidden projects
    queryset = models.Project.objects.order_by('section__division', 'section', 'title')
    filterset_class = filters.ProjectFilter
    home_url_name = "projects2:index"
    container_class = "container-fluid"
    row_object_url_name = "projects2:project_detail"
    h1 = gettext_lazy("Full Project List")
    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'region', "class": "", "width": ""},
        {"name": 'division', "class": "", "width": ""},
        {"name": 'section', "class": "", "width": ""},
        {"name": 'title', "class": "", "width": "400px"},
        {"name": 'default_funding_source', "class": "", "width": ""},
        {"name": 'lead_staff', "class": "", "width": ""},
        {"name": 'tags', "class": "", "width": ""},
    ]


class MyProjectListView(LoginRequiredMixin, CommonListView):
    template_name = 'projects2/project_list.html'
    # filterset_class = filters.MyProjectFilter
    h1 = gettext_lazy("My projects")
    home_url_name = "projects2:index"
    container_class = "container-fluid"
    row_object_url_name = "projects2:project_detail"
    new_object_url = "projects2:project_new"
    field_list = [
        {"name": 'section', "class": "", "width": ""},
        {"name": 'title', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'lead_staff', "class": "", "width": ""},
        {"name": 'has_unsubmitted_years|{}'.format("has unsubmitted years?"), "class": "", "width": ""},
        {"name": 'is_hidden', "class": "", "width": "150px"},
        {"name": 'updated_at', "class": "", "width": ""},
    ]

    # x = [
    #     "recommended_for_funding",
    #     "approved",
    #     "status_report|{}".format("Status reports"),
    # ]

    def get_queryset(self):
        project_ids = [staff.project_year.project_id for staff in self.request.user.staff_instances2.all()]
        return models.Project.objects.filter(id__in=project_ids).order_by("-updated_at", "title")

    # def get_filterset_kwargs(self, filterset_class):
    #     kwargs = super().get_filterset_kwargs(filterset_class)
    #     if kwargs["data"] is None:
    #         kwargs["data"] = {"year": fiscal_year(next=True, sap_style=True)}
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # # Based on the default sorting order, we get the fiscal year from the first project instance
        # object_list = context.get("object_list")  # grab the projects returned by the filter
        # fy = object_list.first().year if object_list.count() > 0 else None
        #
        # staff_instances = self.request.user.staff_instances2.filter(project__year=fy)
        #
        # context['fte_approved_projects'] = staff_instances.filter(
        #     project__recommended_for_funding=True, project__submitted=True
        # ).aggregate(dsum=Sum("duration_weeks"))["dsum"]
        #
        # context['fte_unapproved_projects'] = staff_instances.filter(
        #     project__recommended_for_funding=False, project__submitted=True
        # ).aggregate(dsum=Sum("duration_weeks"))["dsum"]
        #
        # context['fte_unsubmitted_projects'] = staff_instances.filter(
        #     project__submitted=False
        # ).aggregate(dsum=Sum("duration_weeks"))["dsum"]
        #
        # context['fy'] = fy
        #
        # context["project_list"] = models.Project.objects.filter(
        #     id__in=[s.project.id for s in self.request.user.staff_instances.all()]
        # )
        #
        # context["project_field_list"] = [
        #     "year",
        #     "submitted|{}".format("Submitted"),
        #     "recommended_for_funding",
        #     "approved",
        #     "allocated_budget",
        #     "section|Section",
        #     "project_title",
        #     "is_hidden|is this a hidden project?",
        #     "is_lead|{}?".format("Are you a project lead"),
        #     "status_report|{}".format("Status reports"),
        # ]

        return context


class ProjectCreateView(LoginRequiredMixin, CommonCreateView):
    model = models.Project
    form_class = forms.NewProjectForm
    home_url_name = "projects2:index"
    template_name = 'projects2/project_form.html'

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
        my_object = form.save(commit=False)
        # modifications to project instance before saving
        my_object.modified_by = self.request.user
        my_object.save()
        #
        # # create a first year of the project
        # year = models.ProjectYear.objects.create(
        #     project=my_object,
        # )
        # # populate some initial staff and om costs
        # models.Staff.objects.create(
        #     project_year=year,
        #     is_lead=True,
        #     employee_type_id=1,
        #     user_id=self.request.user.id,
        #     funding_source=my_object.default_funding_source
        # )
        # year.add_all_om_costs()
        messages.success(self.request, _("Your new project was created successfully! To get started, <b>add a new project year</b>."))
        return HttpResponseRedirect(reverse_lazy("projects2:project_detail", kwargs={"pk": my_object.id}))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ProjectDetailView(LoginRequiredMixin, CommonDetailView):
    model = models.Project
    template_name = 'projects2/project_detail/project_detail.html'
    home_url_name = "projects2:index"
    container_class = "container-fluid"

    # parent_crumb = {"title": _("My Projects"), "url": reverse_lazy("projects2:my_project_list")}

    def get_active_page_name_crumb(self):
        return str(self.get_object())

    def get_h1(self):
        mystr = str(self.get_object())
        if self.get_object().has_unsubmitted_years:
            mystr += ' <span class="red-font">{}</span>'.format(_("UNSUBMITTED"))
        return mystr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        # If this is a gulf region project, only show the gulf region fields
        context["project_field_list"] = get_project_field_list(project)
        context["project_year_field_list"] = get_project_year_field_list()

        context["staff_form"] = forms.StaffForm
        context["random_staff"] = models.Staff.objects.first()

        context["om_cost_form"] = forms.OMCostForm
        context["random_om_cost"] = models.OMCost.objects.first()

        context["capital_cost_form"] = forms.CapitalCostForm
        context["random_capital_cost"] = models.CapitalCost.objects.first()

        context["gc_cost_form"] = forms.GCCostForm
        context["random_gc_cost"] = models.GCCost.objects.first()

        context["milestone_form"] = forms.MilestoneForm
        context["random_milestone"] = models.Milestone.objects.first()

        context["collaborator_form"] = forms.CollaboratorForm
        context["random_collaborator"] = models.Collaborator.objects.first()

        context["agreement_form"] = forms.AgreementForm
        context["random_agreement"] = models.CollaborativeAgreement.objects.first()

        context["btn_class_1"] = ""
        # context["files"] = project.files.all()
        # context["financial_summary_dict"] = financial_summary_data(project)

        # Determine if the user will be able to edit the project.
        # context["can_edit"] = can_modify_project(self.request.user, project.id)
        # context["is_lead"] = self.request.user in [staff.user for staff in project.staff_members.filter(lead=True)]
        return context


class ProjectUpdateView(CanModifyProjectRequiredMixin, CommonUpdateView):
    model = models.Project
    form_class = forms.ProjectForm
    template_name = 'projects2/project_form.html'
    home_url_name = "projects2:index"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("projects2:project_detail", args=[self.get_object().id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()
        return context

    def get_initial(self):
        return dict(modified_by=self.request.user)


class ProjectDeleteView(CanModifyProjectRequiredMixin, CommonDeleteView):
    model = models.Project
    delete_protection = False
    home_url_name = "projects2:index"
    success_url = reverse_lazy("projects2:index")
    template_name = "projects2/confirm_delete.html"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("projects2:project_detail", args=[self.get_object().id])}


# PROJECT YEAR #
################


class ProjectYearCreateView(CanModifyProjectRequiredMixin, CommonCreateView):
    model = models.ProjectYear
    form_class = forms.ProjectYearForm
    home_url_name = "projects2:index"
    template_name = 'projects2/project_year_form.html'

    def get_initial(self):
        # this is an important method to keep since it is accessed by the Form class 
        # TODO: TEST ME
        return dict(project=self.get_project())

    def get_project(self):
        return models.Project.objects.get(pk=self.kwargs["project"])

    def get_parent_crumb(self):
        return {"title": self.get_project(), "url": reverse_lazy("projects2:project_detail", args=[self.get_project().id])}

    def form_valid(self, form):
        year = form.save(commit=False)
        year.modified_by = self.request.user
        year.save()

        return HttpResponseRedirect(
            super().get_success_url() + f"?project_year={year.id}"
        )


class ProjectYearUpdateView(CanModifyProjectRequiredMixin, CommonUpdateView):
    model = models.ProjectYear
    form_class = forms.ProjectYearForm
    home_url_name = "projects2:index"
    template_name = 'projects2/project_year_form.html'

    def get_h1(self):
        return _("Edit ") + str(self.get_object())

    def get_project(self):
        return self.get_object().project

    def get_parent_crumb(self):
        return {"title": self.get_project(), "url": reverse_lazy("projects2:project_detail", args=[self.get_project().id])}

    def form_valid(self, form):
        year = form.save(commit=False)
        year.modified_by = self.request.user
        year.save()
        return super().form_valid(form)

    def get_success_url(self):
        return super().get_success_url() + f"?project_year={self.get_object().id}"


class ProjectYearDeleteView(CanModifyProjectRequiredMixin, CommonDeleteView):
    model = models.ProjectYear
    delete_protection = False
    home_url_name = "projects2:index"
    template_name = "projects2/confirm_delete.html"

    def get_grandparent_crumb(self):
        return {"title": self.get_project(), "url": reverse("projects2:project_detail", args=[self.get_project().id])}

    def get_project(self):
        return self.get_object().project

    def delete(self, request, *args, **kwargs):
        project = self.get_project()
        self.get_object().delete()
        project.save()
        return HttpResponseRedirect(reverse("projects2:project_detail", args=[project.id]))


class ProjectYearCloneView(ProjectYearUpdateView):
    template_name = 'projects2/project_year_form.html'

    def get_h1(self):
        return _("Cloning: ") + str(self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloning"] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:login_required'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        init = super().get_initial()
        init["start_date"] = timezone.now()
        init["cloning"] = True
        return init

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.ProjectYear.objects.get(pk=new_obj.pk)

        new_obj.pk = None
        new_obj.submitted = None
        new_obj.allocated_budget = None
        new_obj.notification_email_sent = None
        new_obj.save()

        # Now we need to replicate all the related records:
        # 1) staff
        for old_rel_obj in old_obj.staff_set.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # we have to just make sure that the user is a lead on the project. Otherwise they will not be able to edit.
        my_staff, created = models.Staff.objects.get_or_create(
            user=self.request.user,
            project_year=new_obj,
            employee_type_id=1,
        )
        my_staff.lead = True
        my_staff.save()

        # 2) O&M
        for old_rel_obj in old_obj.omcost_set.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # 3) Capital
        for old_rel_obj in old_obj.capitalcost_set.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # 4) G&C
        for old_rel_obj in old_obj.gc_costs.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # 5) Collaborators and Partners
        for old_rel_obj in old_obj.collaborators.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # 6) Collaborative Agreements
        for old_rel_obj in old_obj.agreements.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # 7) Milestones
        for old_rel_obj in old_obj.milestones.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.target_date = None  # clear the target date
            new_rel_obj.save()

        return HttpResponseRedirect(reverse_lazy("projects2:project_detail", kwargs={"pk": new_obj.project.id}))


########################################


class SectionProjectListView(LoginRequiredMixin, CommonListView):
    template_name = 'projects2/section_project_list.html'
    # filterset_class = filters.SectionFilter
    home_url_name = "projects2:index"
    container_class = "container-fluid"

    def get_h1(self):
        return str(shared_models.Section.objects.get(pk=self.kwargs.get("section")))

    def get_queryset(self):
        return models.Project.objects.filter(
            section_id=self.kwargs.get("section")).order_by(
            '-year', 'section__division', 'section', 'project_title')

    # def get_filterset_kwargs(self, filterset_class):
    #     kwargs = super().get_filterset_kwargs(filterset_class)
    #     if kwargs["data"] is None:
    #         kwargs["data"] = {"year": fiscal_year(next=True, sap_style=True)}
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["random_project"] = models.Project.objects.first()
        context["field_list"] = [
            "project_title",
            "functional_group",
            "status",
            "default_funding_source",
            'funding_sources|{}'.format(gettext_lazy("Complete list of funding sources")),
            "activity_type",
            "project_leads|{}".format("Leads"),
            "status_report_count|{}".format(_("Status reports")),
        ]
        # we do this so that we are only grabbing the objects that are passing through the filter
        object_list = context.get("object_list")
        try:
            context['region'] = object_list.first().section.division.branch.region
        except (ValueError, AttributeError):
            # it is possible the object list is empty. in that case, grab the first instance from the qs
            context['region'] = self.get_queryset().first().section.division.branch.region

        section = shared_models.Section.objects.get(pk=self.kwargs.get("section"))
        fy = object_list.first().year if object_list.count() > 0 else None
        context['next_fiscal_year'] = shared_models.FiscalYear.objects.get(pk=fiscal_year(next=True, sap_style=True))
        context['unrecommended_projects'] = object_list.filter(recommended_for_funding=False, submitted=True)
        context['unsubmitted_projects'] = object_list.filter(submitted=False)

        recommended_projects = object_list.filter(recommended_for_funding=True, submitted=True)
        context['recommended_projects'] = recommended_projects

        # need to create a dict for displaying projects by funding source.
        fs_dict = {}
        funding_sources = set([project.default_funding_source for project in recommended_projects])
        for fs in funding_sources:
            fs_dict[fs] = recommended_projects.filter(default_funding_source=fs)
        context['fs_dict'] = fs_dict

        # need to create a dict for displaying projects by functional group.
        fg_dict = {}
        functional_groups = set([project.functional_group for project in recommended_projects])
        for fg in functional_groups:
            fg_dict[fg] = {}
            fg_dict[fg]["projects"] = recommended_projects.filter(functional_group=fg)
            fg_dict[fg]["note"] = models.Note.objects.get_or_create(section=section, functional_group=fg)[0]
        context['fg_dict'] = fg_dict

        # need to create a dict for displaying projects by activity type.
        at_dict = {}
        activity_types = set([project.activity_type for project in recommended_projects])
        for at in activity_types:
            at_dict[at] = recommended_projects.filter(activity_type=at)
        context['at_dict'] = at_dict

        # need to create a staff list dictionary
        user_dict = {}

        user_list = list(
            set([staff.user for project in object_list for staff in project.staff_members.all() if staff.user]))
        user_sort_order = [str(user) if user else "AAA" for user in user_list]
        for user in [x for _, x in sorted(zip(user_sort_order, user_list))]:
            user_dict[user] = {}
            user_dict[user]["qs"] = user.staff_instances.filter(
                project__year=fy
            ).order_by("project__submitted", "project__recommended_for_funding", "lead", "project__project_title")

            user_dict[user]["fte_recommended"] = user.staff_instances.filter(
                project__recommended_for_funding=True, project__submitted=True, project__year=fy
            ).aggregate(dsum=Sum("duration_weeks"))["dsum"]

            user_dict[user]["fte_not_recommended"] = user.staff_instances.filter(
                project__recommended_for_funding=False, project__submitted=True, project__year=fy
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

        # status reports (unreviewed)
        context['status_reports'] = models.StatusReport.objects.filter(project__in=object_list)
        context["status_report_field_list"] = [
            'date_created',
            'created_by',
            'status',
            'section_head_comment',
            'section_head_reviewed',
        ]
        return context


class ProjectOverviewDetailView(ProjectDetailView):

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return 'projects2/project_overview_pop.html'
        else:
            return 'projects2/project_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProjectPrintDetailView(LoginRequiredMixin, PDFTemplateView):
    model = models.Project
    template_name = "projects2/project_report.html"

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


class ProjectSubmitUpdateView(ProjectLeadRequiredMixin, CommonUpdateView):
    model = models.Project
    form_class = forms.ProjectSubmitForm
    home_url_name = "projects2:index"
    submit_text = gettext_lazy("Submit")

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("projects2:project_detail", args=[self.get_object().id])}

    def get_active_page_name_crumb(self):
        if self.get_object().submitted:
            return _("Un-submit")
        else:
            return _("Submit")

    def get_h1(self):
        if self.get_object().submitted:
            return _("Are you sure you want to unsubmit the this project?")
        else:
            return _("Are you sure you want to submit the following project?")

    def get_template_names(self):
        if self.kwargs.get("pop"):
            return "projects2/project_action_form_popout.html"
        else:
            return "projects2/project_submit_form.html"

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
            return HttpResponseRedirect(reverse('projects2:close_me'))
        else:
            # Send out an email only when a project is submitted
            if my_object.submitted:
                # create a new email object
                email = emails.ProjectSubmissionEmail(self.object, self.request)
                # send the email object
                custom_send_mail(
                    subject=email.subject,
                    html_message=email.message,
                    from_email=email.from_email,
                    recipient_list=email.to_list
                )
            messages.success(self.request,
                             _("The project was submitted and an email has been sent to notify the section head!"))
            return HttpResponseRedirect(reverse('projects2:project_detail', kwargs={"pk": my_object.id}))


class ProjectNotesUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
    model = models.Project
    form_class = forms.ProjectNotesForm
    template_name = "projects2/project_action_form_popout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        action = _("Save")
        context["action"] = action
        btn_color = "primary"
        context["btn_color"] = btn_color

        return context

    def form_valid(self, form):
        my_object = form.save()
        return HttpResponseRedirect(reverse('projects2:close_me'))


# class ProjectRecommendationUpdateView(CanModifyProjectRequiredMixin, UpdateView):
#     model = models.Project
#     template_name = "projects2/project_action_form_popout.html"
#     success_url = reverse_lazy("projects2:close_me")
#     form_class = forms.ProjectRecommendationForm
#
#     def get_initial(self):
#         return {
#             'last_modified_by': self.request.user,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         action = _("Un-recommend") if self.object.recommended_for_funding else _("Recommend")
#         context["action"] = action
#         btn_color = "danger" if self.object.recommended_for_funding else "success"
#         context["btn_color"] = btn_color
#         return context
#
#     def form_valid(self, form):
#         my_object = form.save(commit=False)
#         if my_object.recommended_for_funding:
#             my_object.recommended_for_funding = False
#         else:
#             my_object.recommended_for_funding = True
#         my_object.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))


class ProjectCloneUpdateView(ProjectUpdateView):
    template_name = 'projects2/project_form.html'
    h1 = gettext_lazy("Please enter the new project details...")

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
        new_tags = form.cleaned_data.get("tags")
        new_project_codes = form.cleaned_data.get("existing_project_codes")
        new_obj.pk = None
        new_obj.submitted = False
        new_obj.approved = False
        new_obj.recommended_for_funding = False
        new_obj.date_last_modified = timezone.now()
        new_obj.last_modified_by = self.request.user
        new_obj.save()

        # now that the new object has an id, we can add the many 2 many links

        for t in new_tags:
            new_obj.tags.add(t.id)

        for code in new_project_codes:
            new_obj.existing_project_codes.add(code.id)

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

        return HttpResponseRedirect(reverse_lazy("projects2:project_detail", kwargs={"pk": new_obj.id}))


# STAFF #
#########

class StaffCreateView(CanModifyProjectRequiredMixin, CreateView):
    model = models.Staff
    template_name = 'projects2/staff_form_popout.html'
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
            return HttpResponseRedirect(reverse_lazy('projects2:ot_calc', kwargs={"pk": object.id}))
        else:
            return HttpResponseRedirect(reverse('projects2:close_me'))


class StaffUpdateView(CanModifyProjectRequiredMixin, UpdateView):
    model = models.Staff
    template_name = 'projects2/staff_form_popout.html'
    form_class = forms.StaffForm

    def form_valid(self, form):
        object = form.save()
        return HttpResponseRedirect(reverse('projects2:close_me'))

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
        return HttpResponseRedirect(reverse('accounts:denied_access'))


class OverTimeCalculatorTemplateView(LoginRequiredMixin, UpdateView):
    template_name = 'projects2/overtime_calculator_popout.html'
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
        return HttpResponseRedirect(reverse_lazy('projects2:staff_edit', kwargs={"pk": object.id}))


#
# # COLLABORATOR #
# ################
#
# class CollaboratorCreateView(CanModifyProjectRequiredMixin, CreateView):
#     model = models.Collaborator
#     template_name = 'projects2/collaborator_form_popout.html'
#     form_class = forms.CollaboratorForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# class CollaboratorUpdateView(CanModifyProjectRequiredMixin, UpdateView):
#     model = models.Collaborator
#     template_name = 'projects2/collaborator_form_popout.html'
#     form_class = forms.CollaboratorForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# def collaborator_delete(request, pk):
#     object = models.Collaborator.objects.get(pk=pk)
#     if can_modify_project(request.user, object.project.id):
#         object.delete()
#         messages.success(request, _("The collaborator has been successfully deleted from project."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     else:
#         return HttpResponseRedirect(reverse('accounts:denied_access'))
#
#
# # AGREEMENTS #
# ##############
#
# class AgreementCreateView(CanModifyProjectRequiredMixin, CreateView):
#     model = models.CollaborativeAgreement
#     template_name = 'projects2/agreement_form_popout.html'
#     form_class = forms.AgreementForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# class AgreementUpdateView(CanModifyProjectRequiredMixin, UpdateView):
#     model = models.CollaborativeAgreement
#     template_name = 'projects2/agreement_form_popout.html'
#     form_class = forms.AgreementForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# def agreement_delete(request, pk):
#     object = models.CollaborativeAgreement.objects.get(pk=pk)
#     if can_modify_project(request.user, object.project.id):
#         object.delete()
#         messages.success(request, _("The agreement has been successfully deleted."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     else:
#         return HttpResponseRedirect(reverse('accounts:denied_access'))
#
#
# # OM COSTS #
# ############
#
# class OMCostCreateView(CanModifyProjectRequiredMixin, CreateView):
#     model = models.OMCost
#     template_name = 'projects2/cost_form_popout.html'
#     form_class = forms.OMCostForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#             'funding_source': project.default_funding_source,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         context['cost_type'] = "O&M"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# class OMCostUpdateView(CanModifyProjectRequiredMixin, UpdateView):
#     model = models.OMCost
#     template_name = 'projects2/cost_form_popout.html'
#     form_class = forms.OMCostForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['cost_type'] = _("O&M")
#         return context
#
#
# def om_cost_delete(request, pk):
#     object = models.OMCost.objects.get(pk=pk)
#     if can_modify_project(request.user, object.project.id):
#         object.delete()
#         messages.success(request, _("The cost has been successfully deleted."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     else:
#         return HttpResponseRedirect(reverse('accounts:denied_access'))
#
#
# def om_cost_clear(request, project):
#     project = models.Project.objects.get(pk=project)
#     if can_modify_project(request.user, project.id):
#         for obj in models.OMCategory.objects.all():
#             for cost in models.OMCost.objects.filter(project=project, om_category=obj):
#                 print(cost)
#                 if (cost.budget_requested is None or cost.budget_requested == 0) and not cost.description:
#                     cost.delete()
#
#         messages.success(request, _("All empty O&M lines have been cleared."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     else:
#         return HttpResponseRedirect(reverse('accounts:denied_access'))
#
#
# def om_cost_populate(request, project):
#     project = models.Project.objects.get(pk=project)
#     if can_modify_project(request.user, project.id):
#         for obj in models.OMCategory.objects.all():
#             if not models.OMCost.objects.filter(project=project, om_category=obj).count():
#                 new_item = models.OMCost.objects.create(project=project, om_category=obj)
#                 new_item.save()
#
#         messages.success(request, _("All O&M categories have been added to this project."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     else:
#         return HttpResponseRedirect(reverse('accounts:denied_access'))
#
#
# # CAPITAL COSTS #
# #################
#
# class CapitalCostCreateView(CanModifyProjectRequiredMixin, CreateView):
#     model = models.CapitalCost
#     template_name = 'projects2/cost_form_popout.html'
#     form_class = forms.CapitalCostForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#             'funding_source': project.default_funding_source,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         context['cost_type'] = "Capital"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# class CapitalCostUpdateView(CanModifyProjectRequiredMixin, UpdateView):
#     model = models.CapitalCost
#     template_name = 'projects2/cost_form_popout.html'
#     form_class = forms.CapitalCostForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['cost_type'] = "Capital"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# def capital_cost_delete(request, pk):
#     object = models.CapitalCost.objects.get(pk=pk)
#     if can_modify_project(request.user, object.project.id):
#         object.delete()
#         messages.success(request, _("The cost has been successfully deleted."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     else:
#         return HttpResponseRedirect(reverse('accounts:denied_access'))
#
#
# # GC COSTS #
# ############
#
# class GCCostCreateView(CanModifyProjectRequiredMixin, CreateView):
#     model = models.GCCost
#     template_name = 'projects2/cost_form_popout.html'
#     form_class = forms.GCCostForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         context['cost_type'] = "G&C"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# class GCCostUpdateView(CanModifyProjectRequiredMixin, UpdateView):
#     model = models.GCCost
#     template_name = 'projects2/cost_form_popout.html'
#     form_class = forms.GCCostForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['cost_type'] = "G&C"
#         return context
#
#
# def gc_cost_delete(request, pk):
#     object = models.GCCost.objects.get(pk=pk)
#     if can_modify_project(request.user, object.project.id):
#         object.delete()
#         messages.success(request, _("The cost has been successfully deleted."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     else:
#         return HttpResponseRedirect(reverse('accounts:denied_access'))
#
#
# # FILES #
# #########
#
# class FileCreateView(CanModifyProjectRequiredMixin, CreateView):
#     template_name = "projects2/file_form.html"
#     model = models.File
#     form_class = forms.FileForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse("shared_models:close_me"))
#
#     def get_context_data(self, **kwargs):
#         # get context
#         context = super().get_context_data(**kwargs)
#         context["editable"] = True
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         context["project"] = project
#         return context
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         status_report = models.StatusReport.objects.get(pk=self.kwargs['status_report']) if self.kwargs.get(
#             'status_report') else None
#
#         return {
#             'project': project,
#             'status_report': status_report,
#         }
#
#
# class FileUpdateView(CanModifyProjectRequiredMixin, UpdateView):
#     template_name = "projects2/file_form.html"
#     model = models.File
#     form_class = forms.FileForm
#
#     def get_success_url(self, **kwargs):
#         return reverse_lazy("projects2:file_detail", kwargs={"pk": self.object.id})
#
#     def get_context_data(self, **kwargs):
#         # get context
#         context = super().get_context_data(**kwargs)
#         context["editable"] = True
#         return context
#
#
# class FileDetailView(FileUpdateView):
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["editable"] = False
#         return context
#
#
# class FileDeleteView(CanModifyProjectRequiredMixin, DeleteView):
#     template_name = "projects2/file_confirm_delete.html"
#     model = models.File
#
#     def get_success_url(self, **kwargs):
#         return reverse_lazy("shared_models:close_me")
#
#
# # USER #
# ########
#
# # this is a complicated cookie. Therefore we will not use a model view or model form and handle the clean data manually.
# class UserCreateView(LoginRequiredMixin, FormView):
#     form_class = forms.UserCreateForm
#     template_name = 'projects2/user_form.html'
#
#     def get_success_url(self):
#         return reverse_lazy('projects2:close_me')
#
#     def form_valid(self, form):
#         # retrieve data from form
#         first_name = form.cleaned_data['first_name']
#         last_name = form.cleaned_data['last_name']
#         email = form.cleaned_data['email1']
#
#         # create a new user
#         my_user = User.objects.create(
#             username=email,
#             first_name=first_name,
#             last_name=last_name,
#             password="pbkdf2_sha256$120000$ctoBiOUIJMD1$DWVtEKBlDXXHKfy/0wKCpcIDYjRrKfV/wpYMHKVrasw=",
#             is_active=1,
#             email=email,
#         )
#
#         email = emails.UserCreationEmail(my_user, self.request)
#
#         # send the email object
#         custom_send_mail(
#             subject=email.subject,
#             html_message=email.message,
#             from_email=email.from_email,
#             recipient_list=email.to_list
#         )
#         messages.success(self.request, _("The user was created and an email was sent"))
#
#         return super().form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context
#
#


# FUNCTIONAL GROUPS #
#####################

class FunctionalGroupListView(AdminRequiredMixin, CommonFilterView):
    template_name = 'projects2/list.html'
    filterset_class = filters.FunctionalGroupFilter
    home_url_name = "projects2:index"
    new_object_url = "projects2:group_new"
    row_object_url_name = row_ = "projects2:group_edit"

    field_list = [
        {"name": 'tname|{}'.format("name"), "class": "", "width": ""},
        {"name": 'theme', "class": "", "width": ""},
        {"name": 'sections', "class": "", "width": "600px"},
    ]

    def get_queryset(self):
        return models.FunctionalGroup.objects.annotate(
            search_term=Concat('name', Value(" "), 'nom', Value(" "), output_field=TextField()))


class FunctionalGroupUpdateView(AdminRequiredMixin, CommonUpdateView):
    model = models.FunctionalGroup
    form_class = forms.FunctionalGroupForm
    template_name = 'projects2/form.html'
    home_url_name = "projects2:index"
    parent_crumb = {"title": gettext_lazy("Functional Groups"), "url": reverse_lazy("projects2:group_list")}


class FunctionalGroupCreateView(AdminRequiredMixin, CommonCreateView):
    model = models.FunctionalGroup
    form_class = forms.FunctionalGroupForm
    success_url = reverse_lazy('projects2:group_list')
    template_name = 'projects2/form.html'
    home_url_name = "projects2:index"
    parent_crumb = {"title": gettext_lazy("Functional Groups"), "url": reverse_lazy("projects2:group_list")}


class FunctionalGroupDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = models.FunctionalGroup
    success_url = reverse_lazy('projects2:group_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'projects2/confirm_delete.html'


# SETTINGS #
############
class FundingSourceHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.FundingSource
    success_url = reverse_lazy("projects2:manage_funding_sources")


class FundingSourceFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage Funding Source"
    queryset = models.FundingSource.objects.all()
    formset_class = forms.FundingSourceFormset
    success_url = reverse_lazy("projects2:manage_funding_sources")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete_funding_source"


class OMCategoryHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.OMCategory
    success_url = reverse_lazy("projects2:manage_om_cats")


class OMCategoryFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage OMCategory"
    queryset = models.OMCategory.objects.all()
    formset_class = forms.OMCategoryFormset
    success_url = reverse_lazy("projects2:manage_om_cats")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete_om_cat"


class EmployeeTypeHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.EmployeeType
    success_url = reverse_lazy("projects2:manage_employee_types")


class EmployeeTypeFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage Employee Type"
    queryset = models.EmployeeType.objects.all()
    formset_class = forms.EmployeeTypeFormset
    success_url = reverse_lazy("projects2:manage_employee_types")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete_employee_type"


# class StatusHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
#     model = models.Status
#     success_url = reverse_lazy("projects2:manage_statuses")
#
#
# class StatusFormsetView(AdminRequiredMixin, CommonFormsetView):
#     template_name = 'projects2/formset.html'
#     h1 = "Manage Status"
#     queryset = models.Status.objects.all()
#     formset_class = forms.StatusFormset
#     success_url = reverse_lazy("projects2:manage_statuses")
#     home_url_name = "projects2:index"
#     delete_url_name = "projects2:delete_status"
#
#
class TagHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.Tag
    success_url = reverse_lazy("projects2:manage_tags")


class TagFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage Tag"
    queryset = models.Tag.objects.all()
    formset_class = forms.TagFormset
    success_url = reverse_lazy("projects2:manage_tags")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete_tag"

#
class HelpTextHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.HelpText
    success_url = reverse_lazy("projects2:manage_help_text")


class HelpTextFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage Help Text"
    queryset = models.HelpText.objects.all()
    formset_class = forms.HelpTextFormset
    success_url = reverse_lazy("projects2:manage_help_text")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete_help_text"
#
#
class LevelHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.Level
    success_url = reverse_lazy("projects2:manage_levels")


class LevelFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage Level"
    queryset = models.Level.objects.all()
    formset_class = forms.LevelFormset
    success_url = reverse_lazy("projects2:manage_levels")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete_level"
#
#
# # class ProgramHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
# #     model = models.Program
# #     success_url = reverse_lazy("projects2:manage_programs")
# #
# #
# # class ProgramFormsetView(AdminRequiredMixin, CommonFormsetView):
# #     template_name = 'projects2/formset.html'
# #     h1 = "Manage Program"
# #     queryset = models.Program.objects.all()
# #     formset_class = forms.ProgramFormset
# #     success_url = reverse_lazy("projects2:manage_programs")
# #     home_url_name = "projects2:index"
# #     delete_url_name = "projects2:delete_program"
#
#
class ActivityTypeHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.ActivityType
    success_url = reverse_lazy("projects2:manage_activity_types")


class ActivityTypeFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage ActivityType"
    queryset = models.ActivityType.objects.all()
    formset_class = forms.ActivityTypeFormset
    success_url = reverse_lazy("projects2:manage_activity_types")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete_activity_type"
#
#
class ThemeHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.Theme
    success_url = reverse_lazy("projects2:manage_themes")


class ThemeFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage Theme"
    queryset = models.Theme.objects.all()
    formset_class = forms.ThemeFormset
    success_url = reverse_lazy("projects2:manage_themes")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete_theme"
#
#
class UpcomingDateHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.UpcomingDate
    success_url = reverse_lazy("projects2:manage-upcoming-dates")


class UpcomingDateFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'projects2/formset.html'
    h1 = "Manage Upcoming Dates"
    queryset = models.UpcomingDate.objects.all()
    formset_class = forms.UpcomingDateFormset
    success_url = reverse_lazy("projects2:manage-upcoming-dates")
    home_url_name = "projects2:index"
    delete_url_name = "projects2:delete-upcoming-date"
#
#
# class AdminStaffListView(ManagerOrAdminRequiredMixin, FilterView):
#     template_name = 'projects2/admin_staff_list.html'
#     queryset = models.Staff.objects.filter(user__isnull=True).order_by('-project__year', 'project__section__division',
#                                                                        'project__section',
#                                                                        'project__project_title')
#     filterset_class = filters.StaffFilter
#
#
# class AdminStaffUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
#     '''This is really just for the admin view'''
#     model = models.Staff
#     template_name = 'projects2/admin_staff_form.html'
#     form_class = forms.AdminStaffForm
#
#     def form_valid(self, form):
#         my_object = form.save()
#         return HttpResponseRedirect(reverse("projects2:admin_staff_list") + "?" + nz(self.kwargs.get("qry"), ""))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['help_text_dict'] = get_help_text_dict()
#         return context
#
#
# class SubmittedUnapprovedProjectsListView(ManagerOrAdminRequiredMixin, FilterView):
#     template_name = 'projects2/admin_submitted_unapproved_list.html'
#     queryset = models.Project.objects.filter(submitted=True, approved=False).order_by('-year', 'id')
#     filterset_class = filters.AdminSubmittedUnapprovedFilter
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         my_qs = context.get("filter").qs
#         # models.Project.objects.values("section").
#         my_qs = my_qs.values("year_id", "section_id").order_by("year_id", "section_id").distinct().annotate(
#             dcount=Count("id"))
#
#         section_dict = {}
#         for s in shared_models.Section.objects.all():
#             section_dict[s.id] = s
#
#         fy_dict = {}
#         for fy in shared_models.FiscalYear.objects.all():
#             fy_dict[fy.id] = fy
#
#         section_year_program_dict = {}
#         for fy in shared_models.FiscalYear.objects.all():
#             if fy.projects.filter(submitted=True, approved=True).count() > 0:
#                 section_year_program_dict[fy.id] = {}
#                 for s in shared_models.Section.objects.all():
#                     if s.projects.filter(submitted=True, approved=True).count() > 0:
#                         section_year_program_dict[fy.id][s.id] = {}
#                         project_list = context.get("filter").qs.filter(year=fy, section=s)
#                         # section_year_program_dict[fy.id][s.id]["programs"] = \
#                         #     models.Program.objects.filter(projects__in=project_list).distinct()
#
#                         # determine if there are submitted project with no programs
#                         # section_year_program_dict[fy.id][s.id]["program_errors"] = project_list.filter(programs__isnull=True)
#                         section_year_program_dict[fy.id][s.id]["project_list"] = project_list.order_by(
#                             "programs__is_core").distinct()
#
#         context["my_qs"] = my_qs
#         context["section_dict"] = section_dict
#         context["fy_dict"] = fy_dict
#         context["section_year_program_dict"] = section_year_program_dict
#         return context
#
#
# class ProjectApprovalsSearchView(AdminRequiredMixin, CommonFormView):
#     template_name = 'projects2/form.html'
#     form_class = forms.ApprovalQueryBuildForm
#     h1 = gettext_lazy("Find Projects to Approve")
#     home_url_name = "projects2:index"
#     cancel_text = gettext_lazy("Back")
#
#     def form_valid(self, form):
#         region = int(form.cleaned_data.get("region"))
#         fy = int(form.cleaned_data.get("fiscal_year"))
#         return HttpResponseRedirect(reverse("projects2:admin_project_approval", kwargs={"region": region, "fy": fy}))
#
#
# class ProjectApprovalFormsetView(AdminRequiredMixin, CommonFormsetView):
#     template_name = 'projects2/formset.html'
#     formset_class = forms.ProjectApprovalFormset
#     home_url_name = "projects2:index"
#     parent_crumb = {"title": _("Find Projects to Approve"), "url": reverse_lazy("projects2:admin_project_approval_search")}
#     pre_display_fields = ["id", "project_title", "total_cost|total budget requested"]
#     post_display_fields = ["notification_email_sent", ]
#
#     def get_random_object(self):
#         return models.Project.objects.first()
#
#     def get_success_url(self):
#         return reverse("projects2:admin_project_approval", kwargs=self.kwargs)
#
#     def get_queryset(self):
#         return models.Project.objects.filter(
#             recommended_for_funding=True,
#             section__division__branch__region_id=self.kwargs.get("region"),
#             year=self.kwargs.get("fy"),
#             approved__isnull=True,
#         )
#
#     def get_h1(self):
#         region = shared_models.Region.objects.get(pk=self.kwargs.get("region"))
#         fy = shared_models.FiscalYear.objects.get(pk=self.kwargs.get("fy"))
#         return f"Setting Project Approvals for {region} ({fy})"
#
#     def post(self, request, *args, **kwargs):
#         formset = self.formset_class(request.POST, )
#         if formset.is_valid():
#             formset.save()
#             for obj in formset.changed_objects:
#                 obj[0].send_approval_email(request)
#
#             # do something with the formset.cleaned_data
#             messages.success(self.request, "Items have been successfully updated")
#             return HttpResponseRedirect(self.get_success_url())
#             # return self.form_valid(formset)
#         else:
#             return self.render_to_response(self.get_context_data(formset=formset))
#
#
# Reference Materials
class ReferenceMaterialListView(AdminRequiredMixin, CommonListView):
    template_name = "projects2/list.html"
    model = models.ReferenceMaterial
    field_list = [
        {"name": "tname|{}".format(gettext_lazy("name")), "class": "", "width": ""},
        {"name": "region", "class": "", "width": ""},
        {"name": "file_display|{}".format(gettext_lazy("File attachment")), "class": "", "width": ""},
        {"name": "date_created", "class": "", "width": ""},
        {"name": "date_modified", "class": "", "width": ""},
    ]
    new_object_url_name = "projects2:ref_mat_new"
    row_object_url_name = "projects2:ref_mat_edit"
    home_url_name = "projects2:index"
    h1 = gettext_lazy("Reference Materials")


class ReferenceMaterialUpdateView(AdminRequiredMixin, CommonUpdateView):
    model = models.ReferenceMaterial
    form_class = forms.ReferenceMaterialForm
    home_url_name = "projects2:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("projects2:ref_mat_list")}
    template_name = "projects2/form.html"
    is_multipart_form_data = True


class ReferenceMaterialCreateView(AdminRequiredMixin, CommonCreateView):
    model = models.ReferenceMaterial
    form_class = forms.ReferenceMaterialForm
    home_url_name = "projects2:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("projects2:ref_mat_list")}
    template_name = "projects2/form.html"
    is_multipart_form_data = True


class ReferenceMaterialDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = models.ReferenceMaterial
    success_url = reverse_lazy('projects2:ref_mat_list')
    home_url_name = "projects2:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("projects2:ref_mat_list")}
    template_name = "projects2/confirm_delete.html"
    delete_protection = False
#
#
# # STATUS REPORT #
# #################
#
# class StatusReportCreateView(ProjectLeadRequiredMixin, CreateView):
#     model = models.StatusReport
#     template_name = 'projects2/status_report_form_popout.html'
#     form_class = forms.StatusReportForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#             'created_by': self.request.user,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         context['status_report'] = True
#         context['files'] = project.files.all()
#         context["can_edit"] = can_modify_project(self.request.user, project.id)
#         context["is_lead"] = self.request.user in [staff.user for staff in project.staff_members.filter(lead=True)]
#         return context
#
#     def form_valid(self, form):
#         my_object = form.save()
#         return HttpResponseRedirect(reverse_lazy('projects2:report_edit', kwargs={"pk": my_object.id}))
#
#
# class StatusReportUpdateView(ProjectLeadRequiredMixin, UpdateView):
#     model = models.StatusReport
#     template_name = 'projects2/status_report_form_popout.html'
#
#     # form_class = forms.StatusReportForm
#
#     def get_form_class(self):
#         my_project = self.get_object().project
#         if is_section_head(self.request.user, my_project):
#             return forms.StatusReportSectionHeadForm
#         else:
#             return forms.StatusReportForm
#
#     def get_initial(self):
#         return {'created_by': self.request.user, }
#
#     def dispatch(self, request, *args, **kwargs):
#         # when the view loads, let's make sure that all the milestones are on the project.
#         my_object = self.get_object()
#         my_project = my_object.project
#         for milestone in my_project.milestones.all():
#             my_update, created = models.MilestoneUpdate.objects.get_or_create(
#                 milestone=milestone,
#                 status_report=my_object
#             )
#             # if the update is being created, what should be the starting status?
#             # to know, we would have to look and see if there is another report. if there is, we should grab the penultimate report and copy status from there.
#             if created:
#                 # check to see if there is another update on the same milestone. We can do this since milestones are unique to projects.
#                 if milestone.updates.count() > 1:
#                     # if there are more than just 1 (i.e. the one we just created), it will be the second record we are interested in...
#                     last_update = milestone.updates.all()[1]
#                     my_update.status = last_update.status
#                     my_update.save()
#
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = context["object"].project
#         context['status_report'] = self.get_object()
#         context['project'] = project
#         context['files'] = self.get_object().files.all()
#         context["can_edit"] = can_modify_project(self.request.user, project.id)
#         context["is_lead"] = self.request.user in [staff.user for staff in project.staff_members.filter(lead=True)]
#         return context
#
#     def form_valid(self, form):
#         my_object = form.save()
#         return HttpResponseRedirect(reverse_lazy('projects2:report_edit', kwargs={"pk": my_object.id}))
#
#
# class StatusReportDeleteView(CanModifyProjectRequiredMixin, DeleteView):
#     template_name = "projects2/status_report_confirm_delete.html"
#     model = models.StatusReport
#
#     def get_success_url(self, **kwargs):
#         return reverse_lazy("shared_models:close_me")
#
#
# class StatusReportPrintDetailView(LoginRequiredMixin, PDFTemplateView):
#     model = models.Project
#
#     template_name = "projects2/status_report_pdf.html"
#
#     def get_pdf_filename(self):
#         my_report = models.StatusReport.objects.get(pk=self.kwargs["pk"])
#         pdf_filename = "{}.pdf".format(
#             my_report
#         )
#         return pdf_filename
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         my_report = models.StatusReport.objects.get(pk=self.kwargs["pk"])
#         context["object"] = my_report
#         context["report_mode"] = True
#         context['files'] = my_report.files.all()
#
#         context["field_list"] = [
#             'date_created',
#             'created_by',
#             'status',
#             'major_accomplishments',
#             'major_issues',
#             'target_completion_date',
#             'rationale_for_modified_completion_date',
#             'general_comment',
#             'section_head_comment',
#             'section_head_reviewed',
#         ]
#
#         return context
#
#
# # MILESTONE #
# #############
#
# class MilestoneCreateView(ProjectLeadRequiredMixin, CreateView):
#     model = models.Milestone
#     template_name = 'projects2/milestone_form_popout.html'
#     form_class = forms.MilestoneForm
#
#     def get_initial(self):
#         project = models.Project.objects.get(pk=self.kwargs['project'])
#         return {
#             'project': project,
#         }
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = models.Project.objects.get(id=self.kwargs['project'])
#         context['project'] = project
#         # context['cost_type'] = "G&C"
#         return context
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#
# class MilestoneUpdateView(ProjectLeadRequiredMixin, UpdateView):
#     model = models.Milestone
#     template_name = 'projects2/milestone_form_popout.html'
#     form_class = forms.MilestoneForm
#
#     def form_valid(self, form):
#         object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['project'] = context["object"].project
#         return context
#
#
# def milestone_delete(request, pk):
#     object = models.Milestone.objects.get(pk=pk)
#     if can_modify_project(request.user, object.project.id):
#         object.delete()
#         messages.success(request, _("The milestone has been successfully deleted."))
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#
#     else:
#         return HttpResponseRedirect(reverse('accounts:denied_access'))
#
#
# # MILESTONE UPDATE #
# ####################
#
# class MilestoneUpdateUpdateView(UpdateView):
#     model = models.MilestoneUpdate
#     template_name = 'projects2/milestone_form_popout.html'
#     form_class = forms.MilestoneUpdateForm
#
#     def form_valid(self, form):
#         my_object = form.save()
#         return HttpResponseRedirect(reverse('projects2:close_me'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # context['project'] = context["object"].project
#         return context
#
#
# # REPORTS #
# ###########
#
# class ReportSearchFormView(ManagerOrAdminRequiredMixin, FormView):
#     template_name = 'projects2/report_search.html'
#     form_class = forms.ReportSearchForm
#
#     def get_initial(self):
#         # default the year to the year of the latest samples
#         return {"fiscal_year": fiscal_year(next=True, sap_style=True)}
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         print("Search Form Context")
#         division_dict = {}
#         for d in get_division_choices():
#             my_division = shared_models.Division.objects.get(pk=d[0])
#             division_dict[my_division.id] = {}
#             division_dict[my_division.id]["display"] = getattr(my_division, _("name"))
#             division_dict[my_division.id]["region_id"] = my_division.branch.region_id
#
#         section_dict = {}
#         for s in get_section_choices():
#             my_section = shared_models.Section.objects.get(pk=s[0])
#             section_dict[my_section.id] = {}
#             section_dict[my_section.id]["display"] = str(my_section)
#             section_dict[my_section.id]["division_id"] = my_section.division_id
#
#         context['division_json'] = json.dumps(division_dict)
#         context['section_json'] = json.dumps(section_dict)
#         context['omcatagory_json'] = json.dumps(get_omcatagory_choices())
#         return context
#
#     def form_valid(self, form):
#         fiscal_year = str(form.cleaned_data["fiscal_year"])
#         funding = int(form.cleaned_data['funding_src'])
#         report = int(form.cleaned_data["report"])
#         regions = listrify(form.cleaned_data["region"])
#         divisions = listrify(form.cleaned_data["division"])
#         sections = listrify(form.cleaned_data["section"])
#         omcatagory = listrify(form.cleaned_data['omcatagory'])
#
#         if regions == "":
#             regions = "None"
#
#         if divisions == "":
#             divisions = "None"
#
#         if sections == "":
#             sections = "None"
#
#         if omcatagory == "":
#             omcatagory = "None"
#
#         if report == 1:
#             return HttpResponseRedirect(reverse("projects2:report_master", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 2:
#             return HttpResponseRedirect(reverse("projects2:pdf_printout", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 3:
#             return HttpResponseRedirect(reverse("projects2:pdf_project_summary", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 4:
#             return HttpResponseRedirect(reverse("projects2:export_program_list", kwargs={}))
#
#         elif report == 10:
#             return HttpResponseRedirect(reverse("projects2:pdf_fte_summary", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 11:
#             return HttpResponseRedirect(reverse("projects2:pdf_ot", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 12:
#             return HttpResponseRedirect(reverse("projects2:pdf_costs", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 13:
#             return HttpResponseRedirect(reverse("projects2:pdf_collab", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 15:
#             return HttpResponseRedirect(reverse("projects2:pdf_agreements", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 14:
#             return HttpResponseRedirect(reverse("projects2:doug_report", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 17:
#             return HttpResponseRedirect(reverse("projects2:pdf_data", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 18:
#             return HttpResponseRedirect(reverse("projects2:pdf_funding", kwargs={
#                 'funding': funding,
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 19:
#             return HttpResponseRedirect(reverse("projects2:xls_funding", kwargs={
#                 'funding': funding,
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         elif report == 20:
#             return HttpResponseRedirect(reverse("projects2:xls_funding_by_om", kwargs={
#                 'funding': funding,
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#                 'omcatagory': omcatagory,
#             }))
#         elif report == 21:
#             return HttpResponseRedirect(reverse("projects2:xls_covid", kwargs={
#                 'fiscal_year': fiscal_year,
#                 'regions': regions,
#                 'divisions': divisions,
#                 'sections': sections,
#             }))
#         else:
#             messages.error(self.request, "Report is not available. Please select another report.")
#             return HttpResponseRedirect(reverse("projects2:report_search"))
#
#
# def master_spreadsheet(request, fiscal_year, regions=None, divisions=None, sections=None, user=None):
#     # sections arg will be coming in as None from the my_section view
#     if regions is None:
#         regions = "None"
#     if divisions is None:
#         divisions = "None"
#     if sections is None:
#         sections = "None"
#
#     file_url = reports.generate_master_spreadsheet(fiscal_year, regions, divisions, sections, user)
#
#     if os.path.exists(file_url):
#         with open(file_url, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename="Science project planning MASTER LIST {}.xlsx"'.format(
#                 fiscal_year)
#             return response
#     raise Http404
#
#
# def dougs_spreadsheet(request, fiscal_year, regions=None, divisions=None, sections=None):
#     # sections arg will be coming in as None from the my_section view
#     if regions is None:
#         regions = "None"
#     if divisions is None:
#         divisions = "None"
#     if sections is None:
#         sections = "None"
#
#     file_url = reports.generate_dougs_spreadsheet(fiscal_year, regions, divisions, sections)
#
#     if os.path.exists(file_url):
#         with open(file_url, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename="Dougs Spreadsheet {}.xlsx"'.format(
#                 fiscal_year)
#             return response
#     raise Http404
#
#
# class PDFReportTemplate(LoginRequiredMixin, PDFTemplateView):
#     section_list = []
#     division_list = []
#     region_list = []
#
#     project_list = []
#
#     def get_context_data(self, **kwargs):
#
#         context = super().get_context_data(**kwargs)
#
#         mar_id = shared_models.Region.objects.get(name="Maritimes").pk
#         context["fy"] = fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
#         context["approved"] = not (self.kwargs["regions"] == str(mar_id))
#
#         # need to assemble a section list
#         ## first look at the sections arg; if not null, we don't need anything else
#         if self.kwargs["sections"] != "None":
#             self.section_list = shared_models.Section.objects.filter(id__in=self.kwargs["sections"].split(","))
#             self.division_list = shared_models.Division.objects.filter(
#                 id__in=[section.division.id for section in self.section_list])
#             # region_list = shared_models.Region.objects.filter(id__in=[division.region.id for division in division_list])
#         ## next look at the divisions arg; if not null, we don't need anything else
#         elif self.kwargs["divisions"] != "None":
#             self.division_list = shared_models.Division.objects.filter(id__in=self.kwargs["divisions"].split(","))
#             self.section_list = shared_models.Section.objects.filter(division__in=self.division_list)
#             # region_list = shared_models.Region.objects.filter(id__in=[division.region.id for division in division_list])
#         ## next look at the divisions arg; if not null, we don't need anything else
#         elif self.kwargs["regions"] != "None":
#             self.region_list = shared_models.Region.objects.filter(id__in=self.kwargs["regions"].split(","))
#             self.division_list = shared_models.Division.objects.filter(branch__region__in=self.region_list,
#                                                                        branch__id__in=[1, 3])
#             self.section_list = shared_models.Section.objects.filter(division__in=self.division_list)
#
#         # there will always be a section list so let's use that to generate a project list
#         self.project_list = models.Project.objects.filter(year=fy, submitted=True, section_id__in=self.section_list)
#
#         if context["approved"]:
#             self.project_list = self.project_list.filter(approved=True).order_by("id")
#
#         self.project_list = self.project_list.order_by("id")
#
#         return context
#
#
# class PDFFundingReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_funding.html"
#     funding_src = None
#
#     def get_pdf_filename(self):
#         fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
#         pdf_filename = "{} {} Funding Report.pdf".format(fy, self.funding_src)
#         return pdf_filename
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["field_list"] = project_field_list
#
#         funding = int(self.kwargs["funding"])
#         self.funding_src = models.FundingSource.objects.get(pk=funding)
#         context["project_list"] = self.project_list.order_by("project_title").filter(
#             default_funding_source=self.funding_src)
#
#         context["milestone"] = {}
#         context["sal_cost"] = {}
#         context["om_cost"] = {}
#         context["cap_cost"] = {}
#         context['project_leads'] = {}
#         context['total_est'] = {}
#         for project in context["project_list"]:
#             context["milestone"][project.pk] = project.milestones.all()
#             # Filter staff, om and capital cost to make sure we're only getting the component that is related
#             # to what funding source is being reported on
#             context['sal_cost'][project.pk] = \
#                 project.staff_members.filter(funding_source=self.funding_src).aggregate(Sum('cost'))['cost__sum']
#             context['om_cost'][project.pk] = \
#                 project.om_costs.filter(funding_source=self.funding_src).aggregate(Sum('budget_requested'))[
#                     'budget_requested__sum']
#             context['cap_cost'][project.pk] = \
#                 project.capital_costs.filter(funding_source=self.funding_src).aggregate(Sum('budget_requested'))[
#                     'budget_requested__sum']
#
#             context['total_est'][project.pk] = 0
#             context['total_est'][project.pk] += context['sal_cost'][project.pk] if context['sal_cost'][
#                 project.pk] else 0
#             context['total_est'][project.pk] += context['om_cost'][project.pk] if context['om_cost'][project.pk] else 0
#             context['total_est'][project.pk] += context['cap_cost'][project.pk] if context['cap_cost'][
#                 project.pk] else 0
#
#             context['project_leads'][project.pk] = listrify(
#                 [(l.user if l.user else l.name) for l in project.staff_members.all().filter(lead=True)])
#         return context
#
#
# def covid_spreadsheet(request, fiscal_year, regions=None, divisions=None, sections=None):
#     # sections arg will be coming in as None from the my_section view
#     if regions is None:
#         regions = "None"
#     if divisions is None:
#         divisions = "None"
#     if sections is None:
#         sections = "None"
#
#     covid_rpt = reports.CovidReport(regions=regions, divisions=divisions, sections=sections, fiscal_year=fiscal_year)
#     covid_rpt.generate_spread_sheet()
#
#     if os.path.exists(covid_rpt.target_url):
#         with open(covid_rpt.target_url, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename="{} covid.xlsx"'.format(fiscal_year)
#             return response
#     raise Http404
#
#
# def funding_spreadsheet(request, fiscal_year, funding, regions=None, divisions=None, sections=None, omcatagory=None):
#     # sections arg will be coming in as None from the my_section view
#     if regions is None:
#         regions = "None"
#     if divisions is None:
#         divisions = "None"
#     if sections is None:
#         sections = "None"
#
#     file_url = reports.generate_funding_spreadsheet(fiscal_year, funding, regions, divisions, sections, omcatagory)
#
#     funding_src = models.FundingSource.objects.get(pk=funding)
#
#     if os.path.exists(file_url):
#         with open(file_url, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename="{} {} Funding{}.xlsx"'.format(
#                 fiscal_year, funding_src, " By OM Catagory" if omcatagory else "")
#             return response
#     raise Http404
#
#
# class PDFProjectSummaryReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_project_summary.html"
#
#     def get_pdf_filename(self):
#         fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
#         pdf_filename = "{} Project Summary Report.pdf".format(fy)
#         return pdf_filename
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         self.project_list = self.project_list.filter(~Q(feedback=""))
#
#         context["report_mode"] = True
#         context["object_list"] = self.project_list
#         context["field_list"] = project_field_list
#         context["division_list"] = [shared_models.Division.objects.get(pk=item["section__division"]) for item in
#                                     self.project_list.values("section__division").order_by(
#                                         "section__division").distinct()]
#         # bring in financial summary data for each project:
#         context["financial_summary_data"] = {}
#         context["financial_summary_data"]["sections"] = {}
#         context["financial_summary_data"]["divisions"] = {}
#         key_list = [
#             "salary_abase",
#             "salary_bbase",
#             "salary_cbase",
#             "om_abase",
#             "om_bbase",
#             "om_cbase",
#             "capital_abase",
#             "capital_bbase",
#             "capital_cbase",
#             "salary_total",
#             "om_total",
#             "capital_total",
#             "students",
#             "casuals",
#             "OT",
#         ]
#
#         for project in self.project_list:
#             context["financial_summary_data"][project.id] = pdf_financial_summary_data(project)
#             context["financial_summary_data"][project.id]["students"] = project.staff_members.filter(
#                 employee_type=4).count()
#             context["financial_summary_data"][project.id]["casuals"] = project.staff_members.filter(
#                 employee_type=3).count()
#             context["financial_summary_data"][project.id]["OT"] = nz(
#                 project.staff_members.values("overtime_hours").order_by(
#                     "overtime_hours").aggregate(dsum=Sum("overtime_hours"))["dsum"], 0)
#
#             # for sections
#             try:
#                 context["financial_summary_data"]["sections"][project.section.id]
#             except KeyError:
#                 context["financial_summary_data"]["sections"][project.section.id] = {}
#                 # go through the keys and make sure each category is initialized
#                 for key in key_list:
#                     context["financial_summary_data"]["sections"][project.section.id][key] = 0
#             finally:
#                 for key in key_list:
#                     context["financial_summary_data"]["sections"][project.section.id][key] += \
#                         context["financial_summary_data"][project.id][
#                             key]
#
#             # for Divisions
#             try:
#                 context["financial_summary_data"]["divisions"][project.section.division.id]
#             except KeyError:
#                 context["financial_summary_data"]["divisions"][project.section.division.id] = {}
#                 # go through the keys and make sure each category is initialized
#                 for key in key_list:
#                     context["financial_summary_data"]["divisions"][project.section.division.id][key] = 0
#             finally:
#                 for key in key_list:
#                     context["financial_summary_data"]["divisions"][project.section.division.id][key] += \
#                         context["financial_summary_data"][project.id][key]
#
#             # for total
#             try:
#                 context["financial_summary_data"]["total"]
#             except KeyError:
#                 context["financial_summary_data"]["total"] = {}
#                 # go through the keys and make sure each category is initialized
#                 for key in key_list:
#                     context["financial_summary_data"]["total"][key] = 0
#             finally:
#                 for key in key_list:
#                     context["financial_summary_data"]["total"][key] += \
#                         context["financial_summary_data"][project.id][key]
#
#         # get a list of the capital requests
#         context["capital_list"] = [capital_cost for project in self.project_list for capital_cost in
#                                    project.capital_costs.all()]
#
#         # get a list of the G&Cs
#         context["gc_list"] = [gc for project in self.project_list for gc in project.gc_costs.all()]
#
#         # get a list of the collaborators
#         context["collaborator_list"] = [collaborator for project in self.project_list for collaborator in
#                                         project.collaborators.all()]
#
#         # get a list of the agreements
#         context["agreement_list"] = [agreement for project in self.project_list for agreement in
#                                      project.agreements.all()]
#
#         return context
#
#
# class PDFProjectPrintoutReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_printout.html"
#
#     def get_pdf_filename(self):
#         fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
#         pdf_filename = "{} Workplan Export.pdf".format(fy)
#         return pdf_filename
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         context["report_mode"] = True
#         context["object_list"] = self.project_list
#         context["field_list"] = project_field_list
#         context["division_list"] = set([s.division for s in self.section_list])
#         # bring in financial summary data for each project:
#         context["financial_summary_data"] = {}
#         context["financial_summary_data"]["sections"] = {}
#         context["financial_summary_data"]["divisions"] = {}
#         key_list = [
#             "salary_abase",
#             "salary_bbase",
#             "salary_cbase",
#             "om_abase",
#             "om_bbase",
#             "om_cbase",
#             "capital_abase",
#             "capital_bbase",
#             "capital_cbase",
#             "students",
#             "casuals",
#             "OT",
#         ]
#
#         for project in self.project_list:
#             context["financial_summary_data"][project.id] = pdf_financial_summary_data(project)
#
#         return context
#
#
# def workplan_summary(request, fiscal_year):
#     file_url = reports.generate_workplan_summary(fiscal_year)
#
#     if os.path.exists(file_url):
#         with open(file_url, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename="{} Workplan Summary.xlsx"'.format(
#                 fiscal_year)
#             return response
#     raise Http404
#
#
# def export_program_list(request):
#     file_url = reports.generate_program_list()
#
#     if os.path.exists(file_url):
#         with open(file_url, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename="Science Program List.xlsx"'
#             return response
#     raise Http404
#
#
# class PDFCollaboratorReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_collaborators.html"
#
#     # def get_pdf_filename(self):
#     #     fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
#     #     pdf_filename = "{} Project Summary Report.pdf".format(fy)
#     #     return pdf_filename
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         collaborator_list = models.Collaborator.objects.filter(project__in=self.project_list)
#
#         context["object_list"] = collaborator_list
#         context["my_object"] = collaborator_list.first()
#         context["field_list"] = [
#             'name',
#             'critical',
#             'notes',
#             'project',
#         ]
#
#         return context
#
#
# class PDFAgreementsReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_agreements.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         collaborator_list = models.CollaborativeAgreement.objects.filter(project__in=self.project_list)
#
#         context["object_list"] = collaborator_list
#         context["my_object"] = collaborator_list.first()
#         context["field_list"] = [
#             'agreement_title',
#             'partner_organization',
#             'project_lead',
#             'new_or_existing',
#             'project',
#             'notes',
#         ]
#         return context
#
#
# class PDFDataReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_data.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         context["object_list"] = self.project_list
#         context["my_object"] = self.project_list.first()
#         context["field_list"] = [
#             'id',
#             'project_title',
#             'project_leads|Project leads',
#             'data_collection',
#             'data_sharing',
#             'data_storage',
#             'metadata_url',
#             'regional_dm_needs',
#         ]
#
#         return context
#
#
# class PDFFTESummaryReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_fte_summary.html"
#
#     # def get_pdf_filename(self):
#     #     fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
#     #     pdf_filename = "{} Project Summary Report.pdf".format(fy)
#     #     return pdf_filename
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         staff_list = models.Staff.objects.filter(
#             project__in=self.project_list,
#             # employee_type_id__in=[1,]
#             user__isnull=False
#         ).order_by("user__last_name", "user__first_name").values("user").annotate(dsum=Sum("duration_weeks"))
#
#         # users = [models.Staff.objects.get(pk=item["user"]) for item in staff_list]
#         # hours = [item["dsum"] for item in staff_list]
#
#         # context["users"] = users
#         my_dict = {}
#         for i in range(0, len(staff_list)):
#             my_dict[i] = {}
#             my_dict[i]["user"] = User.objects.get(pk=staff_list[i]["user"])
#             my_dict[i]["hours"] = staff_list[i]["dsum"]
#         context["my_dict"] = my_dict
#
#         non_reg_staff_list = models.Staff.objects.filter(user__isnull=True).order_by("name")
#         context["non_reg_staff_list"] = non_reg_staff_list
#
#         return context
#
#
# class PDFOTSummaryReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_ot_summary.html"
#
#     # def get_pdf_filename(self):
#     #     fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
#     #     pdf_filename = "{} Project Summary Report.pdf".format(fy)
#     #     return pdf_filename
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         mar_id = shared_models.Region.objects.get(name="Maritimes").pk
#
#         # NOTE this report is not meant to contain multiple regions...
#         context["division_list"] = self.division_list
#         context["section_list"] = self.section_list
#
#         # bring in financial summary data for each project:
#         my_dict = {}
#         my_dict["total"] = 0
#         my_dict["programs"] = {}
#         for division in self.division_list:
#             # create a sub dict for the division
#             my_dict[division] = {}
#             my_dict[division]["total"] = 0
#             my_dict[division]["nrows"] = 0
#
#             for section in division.sections.all():
#                 # exclude any sections that are not in the section list
#                 if section in self.section_list:
#                     # create a sub sub dict for the section
#
#                     self.project_list = models.Project.objects.filter(year=context['fy'], submitted=True,
#                                                                       section=section)
#                     if context['approved']:
#                         self.project_list = self.project_list.filter(section_head_approved=True)
#
#                     ot = models.Staff.objects.filter(
#                         project__in=self.project_list, overtime_hours__isnull=False,
#                     ).aggregate(dsum=Sum("overtime_hours"))["dsum"]
#                     my_dict[division][section] = {}
#                     my_dict[division][section]["total"] = ot
#                     my_dict[division]["total"] += nz(ot, 0)
#                     my_dict["total"] += nz(ot, 0)
#
#                     # now get the progam list for all the section
#                     program_list = models.Program2.objects.filter(projects__in=self.project_list).distinct()
#                     my_dict[division]["nrows"] += program_list.count()
#                     my_dict[division][section]["programs"] = {}
#                     my_dict[division][section]["programs"]["list"] = program_list
#                     for program in program_list:
#
#                         self.project_list = models.Project.objects.filter(year=context['fy'], submitted=True,
#                                                                           section=section, programs=program)
#                         if context['approved']:
#                             self.project_list = self.project_list.filter(section_head_approved=True)
#
#                         ot = models.Staff.objects.filter(
#                             project__in=self.project_list, overtime_hours__isnull=False,
#                         ).aggregate(dsum=Sum("overtime_hours"))["dsum"]
#
#                         my_dict[division][section]["programs"][program] = ot
#
#                         if not my_dict["programs"].get(program):
#                             my_dict["programs"][program] = 0
#
#                         my_dict["programs"][program] += nz(ot, 0)
#
#         program_list = models.Program2.objects.filter(id__in=[program.id for program in my_dict["programs"]]).distinct()
#         my_dict["programs"]["list"] = program_list
#
#         context["ot_summary_data"] = my_dict
#
#         return context
#
#
# class PDFCostSummaryReport(PDFReportTemplate):
#     template_name = "projects2/report_pdf_cost_summary.html"
#
#     # def get_pdf_filename(self):
#     #     fy = shared_models.FiscalYear.objects.get(pk=self.kwargs["fiscal_year"])
#     #     pdf_filename = "{} Project Summary Report.pdf".format(fy)
#     #     return pdf_filename
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         context["object_list"] = self.project_list
#         context["division_list"] = [shared_models.Division.objects.get(pk=item["section__division"]) for item in
#                                     self.project_list.values("section__division").order_by(
#                                         "section__division").distinct()]
#         # bring in financial summary data for each project:
#         context["financial_summary_data"] = {}
#         context["financial_summary_data"]["sections"] = {}
#         context["financial_summary_data"]["divisions"] = {}
#         key_list = [
#             "salary_abase",
#             "salary_bbase",
#             "salary_cbase",
#             "om_abase",
#             "om_bbase",
#             "om_cbase",
#             "capital_abase",
#             "capital_bbase",
#             "capital_cbase",
#             "salary_total",
#             "om_total",
#             "capital_total",
#             "students",
#             "casuals",
#         ]
#
#         for project in self.project_list:
#             context["financial_summary_data"][project.id] = pdf_financial_summary_data(project)
#             context["financial_summary_data"][project.id]["students"] = project.staff_members.filter(
#                 employee_type=4).count()
#             context["financial_summary_data"][project.id]["casuals"] = project.staff_members.filter(
#                 employee_type=3).count()
#
#             # for sections
#             try:
#                 context["financial_summary_data"]["sections"][project.section.id]
#             except KeyError:
#                 context["financial_summary_data"]["sections"][project.section.id] = {}
#                 # go through the keys and make sure each category is initialized
#                 for key in key_list:
#                     context["financial_summary_data"]["sections"][project.section.id][key] = 0
#             finally:
#                 for key in key_list:
#                     context["financial_summary_data"]["sections"][project.section.id][key] += \
#                         context["financial_summary_data"][project.id][
#                             key]
#
#             # for Divisions
#             try:
#                 context["financial_summary_data"]["divisions"][project.section.division.id]
#             except KeyError:
#                 context["financial_summary_data"]["divisions"][project.section.division.id] = {}
#                 # go through the keys and make sure each category is initialized
#                 for key in key_list:
#                     context["financial_summary_data"]["divisions"][project.section.division.id][key] = 0
#             finally:
#                 for key in key_list:
#                     context["financial_summary_data"]["divisions"][project.section.division.id][key] += \
#                         context["financial_summary_data"][project.id][key]
#
#             # for total
#             try:
#                 context["financial_summary_data"]["total"]
#             except KeyError:
#                 context["financial_summary_data"]["total"] = {}
#                 # go through the keys and make sure each category is initialized
#                 for key in key_list:
#                     context["financial_summary_data"]["total"][key] = 0
#             finally:
#                 for key in key_list:
#                     context["financial_summary_data"]["total"][key] += \
#                         context["financial_summary_data"][project.id][key]
#
#         context["abase"] = models.FundingSourceType.objects.get(pk=1).color
#         context["bbase"] = models.FundingSourceType.objects.get(pk=2).color
#         context["cbase"] = models.FundingSourceType.objects.get(pk=3).color
#         return context
#
#
# # EXTRAS #
# ##########
# class IWGroupList(LoginRequiredMixin, CommonFormView):
#     template_name = 'projects2/iw_group_list.html'
#     form_class = forms.IWForm
#     active_page_name_crumb = gettext_lazy("Functional Group Summary")
#     home_url_name = "projects2:index"
#     h1 = "dud"
#     container_class = "container-fluid"
#
#     def get_initial(self):
#         my_init_dict = dict()
#         my_init_dict["fiscal_year"] = self.kwargs.get("fiscal_year")
#         my_init_dict["region"] = self.kwargs.get("region")
#         my_init_dict["division"] = self.kwargs.get("division")
#         my_init_dict["section"] = self.kwargs.get("section")
#         return my_init_dict
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         fy = shared_models.FiscalYear.objects.get(id=self.kwargs.get("fiscal_year"))
#         context['fy'] = fy
#
#         if self.kwargs.get("region") != 0:
#             my_region = shared_models.Region.objects.get(pk=self.kwargs.get("region"))
#             context['region'] = my_region
#         else:
#             my_region = None
#         if self.kwargs.get("division") != 0:
#             my_division = shared_models.Division.objects.get(pk=self.kwargs.get("division"))
#             context['division'] = my_division
#         else:
#             my_division = None
#         if self.kwargs.get("section") != 0:
#             my_section = shared_models.Section.objects.get(pk=self.kwargs.get("section"))
#             context['section'] = my_section
#         else:
#             my_section = None
#
#         project_list = models.Project.objects.filter(
#             year=fy,
#             submitted=True,
#             recommended_for_funding=True,
#         )
#         if my_section:
#             project_list = project_list.filter(section=my_section)
#         elif my_division:
#             project_list = project_list.filter(section__division=my_division)
#         elif my_region:
#             project_list = project_list.filter(section__division__branch__region=my_region)
#
#         # This view is being retrofitted to be able to show projects by Theme/Program (instead of only by division/section)
#         if self.kwargs.get("type") == "theme":
#             big_list = models.Theme.objects.filter(functional_groups__projects__in=project_list).distinct().order_by()
#             small_list = None
#
#         elif self.kwargs.get("type") == "funding_source":
#             # get a list of all possible funding sources
#             small_list = models.FundingSource.objects.filter(projects__in=project_list).distinct()
#             big_list = models.FundingSourceType.objects.filter(id__in=[fs.funding_source_type_id for fs in small_list])
#
#         # The default sorting is by section
#         else:
#
#             big_list = shared_models.Division.objects.filter(sections__projects__in=project_list).distinct().order_by(
#                 "name")
#             small_list = shared_models.Section.objects.filter(projects__in=project_list).distinct().order_by("division",
#                                                                                                              "name")
#
#         my_dict = {}
#         for big_item in big_list:
#             my_dict[big_item] = {}
#
#             if self.kwargs.get("type") == "theme":
#
#                 my_dict[big_item]['all'] = {}
#                 temp_project_list = project_list.filter(functional_group__theme=big_item)
#                 group_list = set([project.functional_group for project in temp_project_list])
#
#                 my_dict[big_item]['all']["projects"] = temp_project_list
#                 my_dict[big_item]['all']["groups"] = {}
#                 for group in group_list:
#                     my_dict[big_item]['all']["groups"][group] = {}
#
#                     # get a list of project counts
#                     project_count = temp_project_list.filter(functional_group=group).count()
#                     my_dict[big_item]['all']["groups"][group]["project_count"] = project_count
#
#                     # get a list of project leads
#                     leads = listrify(
#                         list(set([str(staff.user) for staff in
#                                   models.Staff.objects.filter(
#                                       project__in=temp_project_list.filter(functional_group=group),
#                                       lead=True) if
#                                   staff.user])))
#                     my_dict[big_item]['all']["groups"][group]["leads"] = leads
#             else:
#                 for small_item in small_list:
#                     # only create an entry for the small item if there are projects within...
#                     add_this_small_item = True
#
#                     if self.kwargs.get("type") == "funding_source":
#                         if project_list.filter(default_funding_source=small_item).count() == 0:
#                             add_this_small_item = False
#                     else:
#                         if project_list.filter(section=small_item).count() == 0:
#                             add_this_small_item = False
#
#                     if add_this_small_item:
#                         if self.kwargs.get("type") == "funding_source":
#                             big_item_name = "funding_source_type"
#                         else:
#                             big_item_name = "division"
#
#                         if getattr(small_item, big_item_name) == big_item:
#                             my_dict[big_item][small_item] = {}
#
#                             # for each section, get a list of projects..  then programs
#                             if self.kwargs.get("type") == "theme":
#                                 temp_project_list = project_list.filter(functional_group__program=small_item)
#                             elif self.kwargs.get("type") == "funding_source":
#                                 temp_project_list = project_list.filter(default_funding_source=small_item)
#                             else:
#                                 temp_project_list = project_list.filter(section=small_item)
#
#                             group_list = set([project.functional_group for project in temp_project_list])
#
#                             my_dict[big_item][small_item]["projects"] = temp_project_list
#                             my_dict[big_item][small_item]["groups"] = {}
#                             for group in group_list:
#                                 my_dict[big_item][small_item]["groups"][group] = {}
#
#                                 # get a list of project counts
#                                 project_count = temp_project_list.filter(functional_group=group).count()
#                                 my_dict[big_item][small_item]["groups"][group]["project_count"] = project_count
#
#                                 # get a list of project leads
#                                 leads = listrify(
#                                     list(set([str(staff.user) for staff in
#                                               models.Staff.objects.filter(
#                                                   project__in=temp_project_list.filter(functional_group=group),
#                                                   lead=True) if
#                                               staff.user])))
#                                 my_dict[big_item][small_item]["groups"][group]["leads"] = leads
#         context['my_dict'] = my_dict
#
#         # projects missing a functional group
#         context['projects_without_groups'] = project_list.filter(functional_group__isnull=True)
#
#         # Only do the following two assessments if we are going by program/theme
#         if self.kwargs.get("type") == "theme":
#             # projects with a program but that are missing a theme
#             context['projects_without_themes'] = project_list.filter(
#                 functional_group__isnull=False,
#                 functional_group__theme__isnull=True).order_by("functional_group")
#
#         context["field_list"] = [
#             "id|{}".format(_("Project Id")),
#             "project_title",
#             "functional_group",
#             "activity_type",
#             "project_leads|{}".format(_("Project leads")),
#         ]
#         context["random_project"] = models.Project.objects.first()
#         return context
#
#     def form_valid(self, form):
#         fy = form.cleaned_data['fiscal_year']
#
#         section = nz(form.cleaned_data['section'], 0)
#         # if the section is known, we should populate the division and region
#         if section != 0:
#             region = shared_models.Section.objects.get(pk=section).division.branch.region.id
#             division = shared_models.Section.objects.get(pk=section).division.id
#         else:
#             division = nz(form.cleaned_data['division'], 0)
#             # if the division is known, we should populate the region
#             if division != 0:
#                 region = shared_models.Division.objects.get(pk=division).branch.region.id
#             else:
#                 region = nz(form.cleaned_data['region'], 0)
#
#         return HttpResponseRedirect(reverse("projects2:iw_group_list", kwargs={
#             "region": region,
#             "division": division,
#             "section": section,
#             "fiscal_year": fy,
#             "type": self.kwargs.get("type"),
#         }))
#
#
# class IWProjectList(ManagerOrAdminRequiredMixin, CommonTemplateView):
#     template_name = 'projects2/iw_project_list.html'
#     h1 = "temp"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         fy = shared_models.FiscalYear.objects.get(id=self.kwargs.get("fiscal_year"))
#
#         # This view is being retrofitted to be able to show projects by Program (instead of only by section)
#         if self.kwargs.get("type") == "theme":
#             small_item = None
#         elif self.kwargs.get("type") == "funding_source":
#             small_item = models.FundingSource.objects.get(id=self.kwargs.get("small_item"))
#         else:
#             small_item = shared_models.Section.objects.get(id=self.kwargs.get("small_item"))
#
#         functional_group = models.FunctionalGroup.objects.get(id=self.kwargs.get("group")) if self.kwargs.get(
#             "group") else None
#         context['fy'] = fy
#         context['small_item'] = small_item
#         context['functional_group'] = functional_group
#
#         # assemble project_list
#         project_list = models.Project.objects.filter(year=fy, submitted=True, recommended_for_funding=True).order_by("id")
#
#         # apply filters from previous view
#         if self.kwargs.get("region") != 0:
#             my_region = shared_models.Region.objects.get(pk=self.kwargs.get("region"))
#             context['region'] = my_region
#         else:
#             my_region = None
#         if self.kwargs.get("division") != 0:
#             my_division = shared_models.Division.objects.get(pk=self.kwargs.get("division"))
#             context['division'] = my_division
#         else:
#             my_division = None
#         if self.kwargs.get("section") != 0:
#             my_section = shared_models.Section.objects.get(pk=self.kwargs.get("section"))
#             context['section'] = my_section
#         else:
#             my_section = None
#
#         if my_section:
#             project_list = project_list.filter(section=my_section)
#         elif my_division:
#             project_list = project_list.filter(section__division=my_division)
#         elif my_region:
#             project_list = project_list.filter(section__division__branch__region=my_region)
#
#         if self.kwargs.get("type") == "theme":
#             project_list = project_list.filter(section__division__branch__region=my_region)
#         elif self.kwargs.get("type") == "funding_source":
#             project_list = project_list.filter(default_funding_source=small_item, section__division__branch__region=my_region)
#         else:
#             project_list = project_list.filter(section=small_item)
#
#         # If a function group is provided keep only those projects
#         if functional_group:
#             project_list = project_list.filter(functional_group=functional_group)
#
#         context['project_list'] = project_list
#         context["field_list"] = [
#             "id|{}".format(_("Project Id")),
#             "project_title",
#             "functional_group",
#             "status",
#             "activity_type",
#             "default_funding_source",
#             # "tags",
#             "project_leads|{}".format(_("Project leads")),
#             "total_fte|{}".format(_("Total FTE")),
#             "total_om|{}".format(_("Total O&M")),
#             "total_salary|{}".format(_("Total salary")),
#             "meeting_notes",
#         ]
#
#         context["financials_dict"] = multiple_projects_financial_summary(project_list)
#
#         # grab a note if available
#         if self.kwargs.get("type") == "theme":
#             try:
#                 context["note"] = models.Note.objects.get_or_create(funding_source=small_item, functional_group=functional_group)[0]
#             except models.Note.MultipleObjectsReturned:
#                 context["note"] = models.Note.objects.filter(section=None, functional_group=functional_group)[0]
#             # anyone looking can edit
#             context["can_edit"] = True
#         elif self.kwargs.get("type") == "funding_source":
#             try:
#                 context["note"] = models.Note.objects.get_or_create(funding_source=small_item, functional_group=functional_group)[0]
#             except models.Note.MultipleObjectsReturned:
#                 context["note"] = models.Note.objects.filter(unding_source=small_item, functional_group=functional_group)[0]
#             # anyone looking can edit
#             context["can_edit"] = True
#         else:
#             try:
#                 context["note"] = models.Note.objects.get_or_create(section=small_item, functional_group=functional_group)[0]
#             except models.Note.MultipleObjectsReturned:
#                 context["note"] = models.Note.objects.filter(section=small_item, functional_group=functional_group)[0]
#             if self.request.user in [small_item.head, small_item.division.head] or in_projects_admin_group(self.request.user):
#                 context["can_edit"] = True
#
#         return context
#
#

#
# # SECTION NOTE #
# ################
#
# class NoteUpdateView(ManagerOrAdminRequiredMixin, UpdateView):
#     model = models.Note
#     template_name = 'projects2/note_form_popout.html'
#     form_class = forms.NoteForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # project = self.get_object()
#         # context["field_list"] = project_field_list
#         # context["report_mode"] = True
#         # context["program"] = models.Program2.objects.get(id=self.kwargs.get("program"))
#         #
#         # bring in financial summary data
#         # my_context = financial_summary_data(project)
#         # context = {**my_context, **context}
#
#         return context
#
#     def form_valid(self, form):
#         my_object = form.save()
#         return HttpResponseRedirect(reverse("shared_models:close_me"))
