from django.test import tag
from django.urls import reverse_lazy

from maret import views
from maret.utils import AdminRequiredMixin
from maret.test.common_tests import CommonMaretTest as CommonTest

from shared_models.views import CommonFormsetView

from faker import Factory

faker = Factory.create()


@tag("formsets")
class TestAllFormsets(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url_names = [
            "manage_topics",
            "manage_species",
            "manage_areas",
        ]
        self.test_urls = [reverse_lazy("maret:" + name) for name in self.test_url_names]
        self.test_views = [
            views.TopicFormsetView,
            views.SpeciesFormsetView,
        ]
        self.expected_template = 'maret/formset.html'
        self.user = self.get_and_login_user(in_group="maret_admin")

    @tag("formsets_view")
    def test_view_class(self):
        for v in self.test_views:
            self.assert_inheritance(v, AdminRequiredMixin)
            self.assert_inheritance(v, CommonFormsetView)

    @tag("formsets_access")
    def test_view(self):
        for url in self.test_urls:
            self.assert_good_response(url)
            self.assert_non_public_view(test_url=url, expected_template=self.expected_template, user=self.user)

    @tag("formsets_submit")
    def test_submit(self):
        data = dict()  # should be fine to submit with empty data
        for url in self.test_urls:
            self.assert_success_url(url, data=data)
