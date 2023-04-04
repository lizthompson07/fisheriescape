from django.urls import reverse_lazy
from django.test import tag

from shared_models.views import CommonCreateView
from fisheriescape import views
from fisheriescape.test import FactoryFloor
from fisheriescape.test.common_tests import CommonFisheriescapeTest as CommonTest

# Example how to run with keyword tags
# python manage.py test fisheriescape.test --tag species_new


#TODO problem with polygon field
class TestFisheryCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FisheryFactory()
        self.test_url = reverse_lazy('fisheriescape:fishery_new')
        self.expected_template = 'fisheriescape/form.html'
        self.user = self.get_and_login_user(in_group="fisheriescape_admin")

    @tag("Fishery", "fishery_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FisheryCreateView, CommonCreateView)
        self.assert_inheritance(views.FisheryCreateView, views.FisheriescapeAdminAccessRequired)

    @tag("Fishery", "fishery_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Fishery", "fishery_new", "submit")
    def test_submit(self):
        data = FactoryFloor.FisheryFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Fishery", "fishery_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("fisheriescape:fishery_new", f"/en/fisheriescape/fishery/new/")
