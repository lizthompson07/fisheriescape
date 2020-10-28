from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from django.views.generic import TemplateView

from cruises.test import FactoryFloor
from cruises.test.common_tests import CommonCruisesTest as CommonTest
from shared_models.views import CommonTemplateView

from .. import views

class TestIndexTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('cruises:index')
        self.expected_template = 'cruises/index.html'
        self.user = self.get_and_login_user()

    @tag("Index", "index", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexTemplateView, TemplateView)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # @tag("Index", "index", "context")
    # def test_context(self):
    #     context_vars = [
    #         "field_list",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Index", "index", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("cruises:index", f"/en/cruises/")