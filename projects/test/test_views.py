from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from django.views.generic import TemplateView

from projects.test import FactoryFloor
from projects.test.common_tests import CommonProjectTest as CommonTest
from .. import views

class TestProjectApprovalFormsetView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectApprovalFactory()
        self.test_url = reverse_lazy('projects:view_name', kwargs={"pk":self.instance.pk})
        self.expected_template = 'projects/template_file_path.html'

    @tag("view_name", 'type', "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProjectApprovalFormsetView, FormsetView)

    @tag("view_name", 'type', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)
        self.assert_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("view_name", 'type', "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)
    
    @tag("view_name", 'type', "submit")
    def test_submit(self):
        data = FactoryFloor.ProjectApprovalFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data)
        
        # for delete views...
        self.assertEqual(models.ProjectApproval.objects.filter(pk=self.instance.pk).count(), 0)