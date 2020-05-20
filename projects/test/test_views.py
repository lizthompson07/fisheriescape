from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from django.views.generic import TemplateView

from projects.test import FactoryFloor
from projects.test.common_tests import CommonProjectTest as CommonTest
from shared_models.views import CommonFormView
from .. import views


class TestProjectApprovalFormsetView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('projects:admin_project_approval_search')
        self.expected_template = 'projects/generic_form.html'
        self.user = self.get_and_login_user(in_group="projects_admin")

    @tag("admin_project_approval_search", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectApprovalsSearchView, CommonFormView)

    @tag("admin_project_approval_search", "access")
    def test_view(self):
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("admin_project_approval_search", "submit")
    def test_submit(self):
        data = {"region": 1, "fy": 2019}
        self.assert_success_url(self.test_url, data=data)

