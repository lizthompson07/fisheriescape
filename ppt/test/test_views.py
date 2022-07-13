from datetime import timedelta, datetime

from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.test import tag
from django.urls import reverse_lazy
from django.utils import timezone
from faker import Factory

from lib.functions.custom_functions import fiscal_year
from shared_models.test.SharedModelsFactoryFloor import UserFactory
from shared_models.views import CommonCreateView, CommonDetailView, CommonUpdateView, CommonDeleteView, CommonListView, CommonTemplateView, CommonFilterView, \
    CommonFormView
from . import FactoryFloor
from .. import views, models
from ..test.common_tests import CommonProjectTest as CommonTest

faker = Factory.create()


class TestACRDPApplicationReportView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse_lazy('ppt:export_acrdp_application', args=[self.instance.id])
        self.user = self.get_and_login_user()

    @tag("Reports", "acrdp-application", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, login_search_term="/accounts/login/")

    @tag("Reports", "acrdp-application", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_acrdp_application", f"/en/ppt/projects/{self.instance.id}/acrdp-application/",
                                test_url_args=[self.instance.id])


class TestACRDPApplicationView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('ppt:export_acrdp_application', args=[self.instance.pk, ])
        self.user = self.get_and_login_user()

    @tag("ACRDPApplication", "export_acrdp_application", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user)

    @tag("ACRDPApplication", "export_acrdp_application", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_acrdp_application", f"/en/ppt/projects/{self.instance.pk}/acrdp-application/",
                                [self.instance.pk])


class TestACRDPBudgetReportView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse_lazy('ppt:export_acrdp_budget', args=[self.instance.id])
        self.user = self.get_and_login_user()

    @tag("Reports", "acrdp-budget", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, login_search_term="/accounts/login/")

    @tag("Reports", "acrdp-budget", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_acrdp_budget", f"/en/ppt/projects/{self.instance.id}/acrdp-budget/",
                                test_url_args=[self.instance.id])


class TestACRDPBugdetView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('ppt:export_acrdp_budget', args=[self.instance.pk, ])
        self.user = self.get_and_login_user()

    @tag("ACRDPApplication", "export_acrdp_budget", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user)

    @tag("ACRDPApplication", "export_acrdp_budget", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_acrdp_budget", f"/en/ppt/projects/{self.instance.pk}/acrdp-budget/",
                                [self.instance.pk])


class TestAdminStaffFilterView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StaffFactory()
        self.test_url = reverse_lazy('ppt:admin_staff_list')
        self.expected_template = 'ppt/admin_staff_list.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("AdminStaff", "admin_staff_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.AdminStaffListView, CommonFilterView)
        self.assert_inheritance(views.AdminStaffListView, views.AdminRequiredMixin)

    @tag("AdminStaff", "admin_staff_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("AdminStaff", "admin_staff_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:admin_staff_list", f"/en/ppt/admin/staff-list/")


class TestAdminStaffUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StaffFactory(name="bobby mcgee", user=None)
        self.test_url = reverse_lazy('ppt:admin_staff_edit', args=[self.instance.pk, ])
        self.test_url1 = reverse_lazy('ppt:admin_staff_edit', args=[self.instance.pk, "?hello_kitty=true"])
        self.expected_template = 'ppt/admin_staff_form.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("AdminStaff", "admin_staff_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.AdminStaffUpdateView, CommonUpdateView)
        self.assert_inheritance(views.AdminStaffUpdateView, views.AdminRequiredMixin)

    @tag("AdminStaff", "admin_staff_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_good_response(self.test_url1)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("AdminStaff", "admin_staff_edit", "context")
    def test_context(self):
        context_vars = [
            "name_count", "match_found"
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("AdminStaff", "admin_staff_edit", "submit")
    def test_submit(self):
        data = None
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("AdminStaff", "admin_staff_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:admin_staff_edit", f"/en/ppt/admin/staff/{self.instance.pk}/edit/", [self.instance.pk])


class TestCSRFApplicationReportView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse_lazy('ppt:csrf_application', args=[self.instance.id])
        self.user = self.get_and_login_user()

    @tag("Reports", "csrf-application", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, login_search_term="/accounts/login/")

    @tag("Reports", "csrf-application", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:csrf_application", f"/en/ppt/projects/{self.instance.id}/csrf-application/",
                                test_url_args=[self.instance.id])


class TestCSRFSubmissionListReportView(CommonTest):
    def setUp(self):
        super().setUp()
        csrf_funding_source = FactoryFloor.FundingSourceFactory(name="CSRF")
        date = datetime(year=faker.pyint(2000, 2030), month=4, day=1, tzinfo=timezone.get_current_timezone())
        year = fiscal_year(date, sap_style=True)
        for i in range(0, 10):
            p = FactoryFloor.ProjectFactory(default_funding_source=csrf_funding_source)
            FactoryFloor.ProjectYearFactory(project=p, start_date=date)
        self.test_url = reverse_lazy('ppt:export_csrf_submission_list') + f'?year={year}&region=None'
        self.user = self.get_and_login_user()

    @tag("Reports", "csrf-submission-list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, login_search_term="/accounts/login/")

    @tag("Reports", "csrf-submission-list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_csrf_submission_list", f"/en/ppt/reports/csrf-submission-list/")


class TestCultureCommitteeReportView(CommonTest):
    def setUp(self):
        super().setUp()
        for i in range(0, 5):
            FactoryFloor.ProjectYearFactory()
        self.test_url = reverse_lazy('ppt:culture_committee_report')
        self.user = self.get_and_login_user()

    @tag("Reports", "culture_committee_report", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user)

    @tag("Reports", "culture_committee_report", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:culture_committee_report", f"/en/ppt/reports/science-culture-committee-report/")


class TestProjectListReportView(CommonTest):
    def setUp(self):
        super().setUp()
        for i in range(0, 5):
            FactoryFloor.ProjectYearFactory()
        self.test_url = reverse_lazy('ppt:export_project_list')
        self.user = self.get_and_login_user()

    @tag("Reports", "export_project_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user)

    @tag("Reports", "export_project_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_project_list", f"/en/ppt/reports/project-list/")


class TestFunctionalGroupCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:group_new')
        self.expected_template = 'ppt/form.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("FunctionalGroup", "group_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FunctionalGroupCreateView, CommonCreateView)

    @tag("FunctionalGroup", "group_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FunctionalGroup", "group_new", "submit")
    def test_submit(self):
        data = FactoryFloor.FunctionalGroupFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user, file_field_name="file_en")

    @tag("FunctionalGroup", "group_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:group_new", f"/en/ppt/settings/functional-groups/new/")


class TestFunctionalGroupDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FunctionalGroupFactory()
        self.test_url = reverse_lazy('ppt:group_delete', args=[self.instance.pk, ])
        self.expected_template = 'ppt/confirm_delete.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("FunctionalGroup", "group_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FunctionalGroupDeleteView, CommonDeleteView)

    @tag("FunctionalGroup", "group_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FunctionalGroup", "group_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.FunctionalGroupFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.FunctionalGroup.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("FunctionalGroup", "group_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:group_delete", f"/en/ppt/settings/functional-groups/{self.instance.pk}/delete/", [self.instance.pk])


class TestFunctionalGroupListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FunctionalGroupFactory()
        self.test_url = reverse_lazy('ppt:group_list')
        self.expected_template = 'ppt/list.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("FunctionalGroup", "group_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FunctionalGroupListView, CommonFilterView)
        self.assert_inheritance(views.FunctionalGroupListView, views.AdminRequiredMixin)

    @tag("FunctionalGroup", "group_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FunctionalGroup", "group_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:group_list", f"/en/ppt/settings/functional-groups/")


class TestFunctionalGroupUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FunctionalGroupFactory()
        self.test_url = reverse_lazy('ppt:group_edit', args=[self.instance.pk, ])
        self.expected_template = 'ppt/form.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("FunctionalGroup", "group_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FunctionalGroupUpdateView, CommonUpdateView)

    @tag("FunctionalGroup", "group_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FunctionalGroup", "group_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.FunctionalGroupFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("FunctionalGroup", "group_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:group_edit", f"/en/ppt/settings/functional-groups/{self.instance.pk}/edit/", [self.instance.pk])


class TestIndexTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:index')
        self.expected_template = 'ppt/index.html'
        self.user = self.get_and_login_user()

    @tag("Index", "index", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexTemplateView, CommonTemplateView)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Index", "index", "context")
    def test_context(self):
        context_vars = [
            "is_management_or_admin",
            "reference_materials",
            "upcoming_dates",
            "past_dates",
            "upcoming_dates_field_list",
        ]

    @tag("Index", "index", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:index", f"/en/ppt/")


class TestProjectCloneView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('ppt:project_clone', args=[self.instance.pk, ])
        self.expected_template = 'ppt/project_form.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_clone", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectCloneView, views.ProjectUpdateView)

    @tag("Project", "project_clone", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Project", "project_clone", "context")
    def test_context(self):
        context_vars = [
            "cloning",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Project", "project_clone", "submit")
    def test_submit(self):
        data = FactoryFloor.ProjectFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Project", "project_clone", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:project_clone", f"/en/ppt/projects/{self.instance.pk}/clone/", [self.instance.pk])


class TestProjectCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:project_new')
        self.expected_template = 'ppt/project_form.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectCreateView, CommonCreateView)

    @tag("Project", "project_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Project", "project_new", "context")
    def test_context(self):
        context_vars = [
            "help_text_dict",
            "division_json",
            "section_json",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Project", "project_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:project_new", f"/en/ppt/projects/new/")


class TestProjectDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('ppt:project_delete', args=[self.instance.pk, ])
        self.expected_template = 'ppt/confirm_delete.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectDeleteView, CommonDeleteView)

    @tag("Project", "project_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Project", "project_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ProjectFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Project.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Project", "project_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:project_delete", f"/en/ppt/projects/{self.instance.pk}/delete/", [self.instance.pk])


class TestProjectDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('ppt:project_detail', args=[self.instance.pk, ])
        self.expected_template = 'ppt/project_detail/main.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectDetailView, CommonDetailView)

    @tag("Project", "project_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Project", "project_detail", "context")
    def test_context(self):
        context_vars = [
            "project_field_list",
            "project_year_field_list",
            "staff_form",
            "random_staff",
            "om_cost_form",
            "random_om_cost",
            "capital_cost_form",
            "random_capital_cost",
            "activity_form",
            "random_activity",
            "collaboration_form",
            "random_collaboration",
            "status_report_form",
            "random_status_report",
            "file_form",
            "random_file",
            "btn_class_1",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Project", "project_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:project_detail", f"/en/ppt/projects/{self.instance.pk}/view/", [self.instance.pk])


class TestProjectExploreTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:explore_projects')
        self.expected_template = 'ppt/explore_projects/main.html'
        self.user = self.get_and_login_user()

    @tag("Project", "explore_projects", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ExploreProjectsTemplateView, CommonTemplateView)

    @tag("Project", "explore_projects", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Project", "explore_projects", "context")
    def test_context(self):
        context_vars = [
            "random_project",
            "status_choices",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Project", "explore_projects", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:explore_projects", f"/en/ppt/projects/explore/")


class TestProjectListView(CommonTest):  # My Projects
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:my_project_list')
        self.expected_template = 'ppt/my_project_list.html'
        self.user = self.get_and_login_user()

    @tag("Project", "my_project_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.MyProjectListView, CommonFilterView)

    @tag("Project", "my_project_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # @tag("Project", "my_project_list", "context")
    # def test_context(self):
    #     context_vars = [
    #         "field_list",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Project", "my_project_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:my_project_list", f"/en/ppt/my-list/")


class TestProjectManageTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:manage_projects')
        self.expected_template = 'ppt/manage_projects/main.html'
        self.user1 = self.get_and_login_user(in_national_admin_group=True)
        self.user2 = FactoryFloor.ProjectFactory().section.head

    @tag("Project", "manage_projects", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ExploreProjectsTemplateView, CommonTemplateView)

    @tag("Project", "manage_projects", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user1)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user2)

    @tag("Project", "manage_projects", "context")
    def test_context(self):
        context_vars = [
            "random_project",
            "status_choices",
            "review_form",
            "approval_form",
            "review_score_rubric",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user1)
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user2)

    @tag("Project", "manage_projects", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:manage_projects", f"/en/ppt/projects/manage/")


class TestProjectStatusSummaryReportView(CommonTest):
    def setUp(self):
        super().setUp()
        date = datetime(year=faker.pyint(2000, 2030), month=4, day=1, tzinfo=timezone.get_current_timezone())
        year = fiscal_year(date, sap_style=True)
        for i in range(0, 10):
            FactoryFloor.ProjectYearFactory(start_date=date)
        self.test_url = reverse_lazy('ppt:export_project_status_summary') + f'?year={year}&region=None'
        self.user = self.get_and_login_user()

    @tag("Reports", "project-status-summary", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, login_search_term="/accounts/login/")

    @tag("Reports", "project-status-summary", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_project_status_summary", f"/en/ppt/reports/project-status-summary/")


class TestProjectUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('ppt:project_edit', args=[self.instance.pk, ])
        self.expected_template = 'ppt/project_form.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectUpdateView, CommonUpdateView)

    @tag("Project", "project_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Project", "project_edit", "context")
    def test_context(self):
        context_vars = [
            "help_text_dict",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Project", "project_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ProjectFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Project", "project_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:project_edit", f"/en/ppt/projects/{self.instance.pk}/edit/", [self.instance.pk])


class TestProjectYearCloneView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse_lazy('ppt:year_clone', args=[self.instance.pk, ])
        self.expected_template = 'ppt/project_year_form.html'
        self.user = self.get_and_login_user()

    @tag("ProjectYear", "year_clone", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectYearCloneView, views.ProjectYearUpdateView)

    @tag("ProjectYear", "year_clone", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ProjectYear", "year_clone", "context")
    def test_context(self):
        context_vars = [
            "cloning",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("ProjectYear", "year_clone", "submit")
    def test_submit(self):
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        # let's manually update the start date so that there is no chance of an invalid form
        data["start_date"] = self.instance.start_date + timedelta(days=366)
        data["end_date"] = ""
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ProjectYear", "year_clone", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:year_clone", f"/en/ppt/project-years/{self.instance.pk}/clone/", [self.instance.pk])


class TestProjectYearCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('ppt:year_new', args=[self.instance.pk, ])
        self.expected_template = 'ppt/project_year_form.html'
        self.user = self.get_and_login_user()

    @tag("ProjectYear", "year_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectYearCreateView, CommonCreateView)

    @tag("ProjectYear", "year_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ProjectYear", "year_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ProjectYear", "year_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:year_new", f"/en/ppt/projects/{self.instance.pk}/new-project-year/", [self.instance.pk])


class TestProjectYearDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse_lazy('ppt:year_delete', args=[self.instance.pk, ])
        self.expected_template = 'ppt/confirm_delete.html'
        self.user = self.get_and_login_user()

    @tag("ProjectYear", "year_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectYearDeleteView, CommonDeleteView)

    @tag("ProjectYear", "year_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ProjectYear", "year_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.ProjectYear.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("ProjectYear", "year_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:year_delete", f"/en/ppt/project-years/{self.instance.pk}/delete/", [self.instance.pk])


class TestProjectYearUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse_lazy('ppt:year_edit', args=[self.instance.pk, ])
        self.expected_template = 'ppt/project_year_form.html'
        self.user = self.get_and_login_user()

    @tag("ProjectYear", "year_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectYearUpdateView, CommonUpdateView)

    @tag("ProjectYear", "year_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ProjectYear", "year_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ProjectYear", "year_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:year_edit", f"/en/ppt/project-years/{self.instance.pk}/edit/", [self.instance.pk])


class TestReferenceMaterialCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:ref_mat_new')
        self.expected_template = 'ppt/form.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("ReferenceMaterial", "ref_mat_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReferenceMaterialCreateView, CommonCreateView)

    @tag("ReferenceMaterial", "ref_mat_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ReferenceMaterialFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user, file_field_name="file_en")

    @tag("ReferenceMaterial", "ref_mat_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:ref_mat_new", f"/en/ppt/settings/reference-materials/new/")


class TestReferenceMaterialDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReferenceMaterialFactory()
        self.test_url = reverse_lazy('ppt:ref_mat_delete', args=[self.instance.pk, ])
        self.expected_template = 'ppt/confirm_delete.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("ReferenceMaterial", "ref_mat_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReferenceMaterialDeleteView, CommonDeleteView)

    @tag("ReferenceMaterial", "ref_mat_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ReferenceMaterialFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.ReferenceMaterial.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("ReferenceMaterial", "ref_mat_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:ref_mat_delete", f"/en/ppt/settings/reference-materials/{self.instance.pk}/delete/", [self.instance.pk])


class TestReferenceMaterialListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReferenceMaterialFactory()
        self.test_url = reverse_lazy('ppt:ref_mat_list')
        self.expected_template = 'ppt/list.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("ReferenceMaterial", "ref_mat_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReferenceMaterialListView, CommonListView)
        self.assert_inheritance(views.ReferenceMaterialListView, views.AdminRequiredMixin)

    @tag("ReferenceMaterial", "ref_mat_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:ref_mat_list", f"/en/ppt/settings/reference-materials/")


class TestReferenceMaterialUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReferenceMaterialFactory()
        self.test_url = reverse_lazy('ppt:ref_mat_edit', args=[self.instance.pk, ])
        self.expected_template = 'ppt/form.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("ReferenceMaterial", "ref_mat_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReferenceMaterialUpdateView, CommonUpdateView)

    @tag("ReferenceMaterial", "ref_mat_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ReferenceMaterialFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:ref_mat_edit", f"/en/ppt/settings/reference-materials/{self.instance.pk}/edit/", [self.instance.pk])


class TestReportSearchFormView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:reports')
        self.expected_template = 'ppt/report_search.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("ReportSearch", "reports", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReportSearchFormView, CommonFormView)
        self.assert_inheritance(views.ReportSearchFormView, views.AdminRequiredMixin)

    @tag("ReportSearch", "reports", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReportSearch", "reports", "submit")
    def test_submit(self):
        data = dict(report=1)
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ReportSearch", "reports", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:reports", f"/en/ppt/reports/")


@tag("ManagementReport")
class TestManagementSearchFormView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ppt:management_reports', args=('pop',))
        self.expected_template = 'ppt/management_search.html'
        self.user = self.get_and_login_user(in_national_admin_group=True)

    @tag("reports", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ManagementReportSearchFormView, CommonFormView)
        self.assert_inheritance(views.ManagementReportSearchFormView, views.AdminRequiredMixin)

    @tag("reports", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # The management view reports should return an HttpResponse so it should return a 200
    # this is unlike the Report Search view which returns reports as a redirection response
    @tag("reports", "submit")
    def test_submit(self):
        data = dict(report=1)
        self.assert_success_url(self.test_url, data=data, user=self.user, expected_code=200)

    @tag("reports", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:management_reports", f"/en/ppt/reports/management/pop/",
                                test_url_args=('pop',))


class TestStatusReportDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StatusReportFactory()
        self.test_url = reverse_lazy('ppt:report_delete', args=[self.instance.pk, ])
        self.expected_template = 'ppt/confirm_delete.html'
        self.user = self.get_and_login_user()

    @tag("StatusReport", "report_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.StatusReportDeleteView, CommonDeleteView)

    @tag("StatusReport", "report_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("StatusReport", "report_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.StatusReportFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)
        # for delete views...
        self.assertEqual(models.StatusReport.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("StatusReport", "report_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:report_delete", f"/en/ppt/status-reports/{self.instance.pk}/delete/", [self.instance.pk])


class TestStatusReportDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StatusReportFactory()
        self.test_url = reverse_lazy('ppt:report_detail', args=[self.instance.pk, ])
        self.expected_template = 'ppt/status_report/main.html'
        self.user = self.get_and_login_user()

    @tag("StatusReport", "report_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.StatusReportDetailView, CommonDetailView)

    @tag("StatusReport", "report_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("StatusReport", "report_detail", "access")
    def test_makes_updates(self):
        # create a bunch of milestones
        m1 = FactoryFloor.ActivityFactory(project_year=self.instance.project_year)
        # there should be no updates...
        self.assertFalse(m1.updates.exists())
        # visit the detail page
        self.assert_good_response(self.test_url)
        self.assertEqual(m1.updates.count(), 1)

    @tag("StatusReport", "report_detail", "context")
    def test_context(self):
        context_vars = [
            "files",
            "file_form",
            "random_file",
            "update_form",
            "random_update",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("StatusReport", "report_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:report_detail", f"/en/ppt/status-reports/{self.instance.pk}/view/", [self.instance.pk])


class TestStatusReportPrintView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StatusReportFactory()
        self.test_url = reverse_lazy('ppt:report_pdf', args=[self.instance.pk, ])
        self.expected_template = 'ppt/status_report_pdf.html'
        self.user = self.get_and_login_user()

    @tag("StatusReport", "report_pdf", "view")
    def test_view_class(self):
        self.assert_inheritance(views.StatusReportPrintDetailView, CommonDetailView)

    @tag("StatusReport", "report_pdf", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("StatusReport", "report_pdf", "context")
    def test_context(self):
        context_vars = [
            "random_file",
            "random_update",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("StatusReport", "report_pdf", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:report_pdf", f"/en/ppt/status-reports/{self.instance.pk}/print/", [self.instance.pk])


class TestStatusReportReviewUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StatusReportFactory()
        self.test_url = reverse_lazy('ppt:report_review', args=[self.instance.pk, ])
        self.expected_template = 'ppt/form.html'
        self.user = self.instance.project_year.project.section.head

    @tag("StatusReport", "report_review", "view")
    def test_view_class(self):
        self.assert_inheritance(views.StatusReportReviewUpdateView, views.StatusReportUpdateView)

    @tag("StatusReport", "report_review", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("StatusReport", "report_review", "submit")
    def test_submit(self):
        data = FactoryFloor.StatusReportFactory.get_valid_review_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("StatusReport", "report_review", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:report_review", f"/en/ppt/status-reports/{self.instance.pk}/review/", [self.instance.pk])


class TestStatusReportUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StatusReportFactory()
        self.test_url = reverse_lazy('ppt:report_edit', args=[self.instance.pk, ])
        self.expected_template = 'ppt/form.html'
        self.user = self.get_and_login_user()

    @tag("StatusReport", "report_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.StatusReportUpdateView, CommonUpdateView)

    @tag("StatusReport", "report_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("StatusReport", "report_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.StatusReportFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("StatusReport", "report_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:report_edit", f"/en/ppt/status-reports/{self.instance.pk}/edit/", [self.instance.pk])


@tag("Reports", "sar_workplan")
class TestSARWorkplanReportView(CommonTest):
    def setUp(self):
        super().setUp()

        date = datetime(year=faker.pyint(2000, 2030), month=4, day=1, tzinfo=timezone.get_current_timezone())
        year = fiscal_year(date, sap_style=True)
        for i in range(0, 10):
            FactoryFloor.ProjectYearFactory(start_date=date)

        # At a minimum a year is required
        self.test_url = reverse_lazy('ppt:export_sar_workplan') + f'?year={year}'

        # tests for year and region (region=1 => Gulf)
        self.test_url_yr = reverse_lazy('ppt:export_sar_workplan') + f'?year={year};region=1'

        self.user = self.get_and_login_user()

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_good_response(self.test_url_yr)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, login_search_term="/accounts/login/")

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_sar_workplan",
                                f"/en/ppt/reports/sar-workplan/")


@tag("Reports", "rsa_report")
class TestRegionalStaffAllocationReportView(CommonTest):
    def setUp(self):
        super().setUp()

        date = datetime(year=faker.pyint(2000, 2030), month=4, day=1, tzinfo=timezone.get_current_timezone())
        year = fiscal_year(date, sap_style=True)
        for i in range(0, 10):
            FactoryFloor.ProjectYearFactory(start_date=date)

        # At a minimum a year is required
        self.test_url = reverse_lazy('ppt:export_rsa') + f'?year={year}&region=1'

        self.user = self.get_and_login_user()

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, login_search_term="/accounts/login/")

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("ppt:export_rsa",
                                f"/en/ppt/reports/regional-staff-allocation/")
