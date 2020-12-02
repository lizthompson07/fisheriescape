from django.test import tag
from django.urls import reverse_lazy
from faker import Factory

from shared_models.views import CommonCreateView, CommonDetailView, CommonUpdateView, CommonDeleteView, CommonListView, CommonTemplateView
from . import FactoryFloor
from .. import views, models
from ..test.common_tests import CommonProjectTest as CommonTest

faker = Factory.create()


class TestProjectCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('projects2:project_new')
        self.expected_template = 'projects2/project_form.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectCreateView, CommonCreateView)

    @tag("Project", "project_new", "access")
    def test_view(self):
        self.assert_valid_url(self.test_url)
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
        self.assert_correct_url("projects2:project_new", f"/en/project-planning/projects/new/")


class TestProjectDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('projects2:project_detail', args=[self.instance.pk, ])
        self.expected_template = 'projects2/project_detail/main.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectDetailView, CommonDetailView)

    @tag("Project", "project_detail", "access")
    def test_view(self):
        self.assert_valid_url(self.test_url)
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
            "gc_cost_form",
            "random_gc_cost",
            "activity_form",
            "random_activity",
            "collaborator_form",
            "random_collaborator",
            "agreement_form",
            "random_agreement",
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
        self.assert_correct_url("projects2:project_detail", f"/en/project-planning/projects/{self.instance.pk}/view/", [self.instance.pk])


class TestProjectUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('projects2:project_edit', args=[self.instance.pk, ])
        self.expected_template = 'projects2/project_form.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectUpdateView, CommonUpdateView)

    @tag("Project", "project_edit", "access")
    def test_view(self):
        self.assert_valid_url(self.test_url)
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
        self.assert_correct_url("projects2:project_edit", f"/en/project-planning/projects/{self.instance.pk}/edit/", [self.instance.pk])


class TestProjectDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('projects2:project_delete', args=[self.instance.pk, ])
        self.expected_template = 'projects2/confirm_delete.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectDeleteView, CommonDeleteView)

    @tag("Project", "project_delete", "access")
    def test_view(self):
        self.assert_valid_url(self.test_url)
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
        self.assert_correct_url("projects2:project_delete", f"/en/project-planning/projects/{self.instance.pk}/delete/", [self.instance.pk])


class TestProjectCloneView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse_lazy('projects2:project_clone', args=[self.instance.pk, ])
        self.expected_template = 'projects2/project_form.html'
        self.user = self.get_and_login_user()

    @tag("Project", "project_clone", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectCloneView, views.ProjectUpdateView)

    @tag("Project", "project_clone", "access")
    def test_view(self):
        self.assert_valid_url(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user,
                                    login_search_term='/accounts/login_required')

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
        self.assert_correct_url("projects2:project_clone", f"/en/project-planning/projects/{self.instance.pk}/clone/", [self.instance.pk])


class TestProjectListView(CommonTest):  # My Projects
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('projects2:my_project_list')
        self.expected_template = 'projects2/my_project_list.html'
        self.user = self.get_and_login_user()

    @tag("Project", "my_project_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.MyProjectListView, CommonListView)

    @tag("Project", "my_project_list", "access")
    def test_view(self):
        self.assert_valid_url(self.test_url)
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
        self.assert_correct_url("projects2:my_project_list", f"/en/project-planning/my-list/")


class TestProjectExploreTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('projects2:explore_projects')
        self.expected_template = 'projects2/explore_projects/main.html'
        self.user = self.get_and_login_user()

    @tag("Project", "explore_projects", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ExploreProjectsTemplateView, CommonTemplateView)

    @tag("Project", "explore_projects", "access")
    def test_view(self):
        self.assert_valid_url(self.test_url)
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
        self.assert_correct_url("projects2:explore_projects", f"/en/project-planning/projects/explore/")


class TestProjectManageTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('projects2:manage_projects')
        self.expected_template = 'projects2/manage_projects/main.html'
        self.user1 = self.get_and_login_user(in_group="projects_admin")
        self.user2 = FactoryFloor.ProjectFactory().section.head



    @tag("Project", "manage_projects", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ExploreProjectsTemplateView, CommonTemplateView)

    @tag("Project", "manage_projects", "access")
    def test_view(self):
        self.assert_valid_url(self.test_url)
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
        self.assert_correct_url("projects2:manage_projects", f"/en/project-planning/projects/manage/")
