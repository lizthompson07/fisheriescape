from django.test import tag
from django.urls import reverse_lazy

from projects.test.common_tests import CommonProjectTest as CommonTest
from shared_models.test.SharedModelsFactoryFloor import RegionFactory
from shared_models.views import CommonFormView, CommonFormsetView, CommonCreateView
from . import FactoryFloor
from .. import views, models
from shared_models import models as shared_models
from faker import Factory

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

