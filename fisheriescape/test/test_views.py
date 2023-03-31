from django.test import tag
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from fisheriescape import views
from fisheriescape.test import FactoryFloor
from fisheriescape.test.common_tests import CommonFisheriescapeTest as CommonTest
from shared_models.views import CommonTemplateView


class TestIndexView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('fisheriescape:index')
        self.expected_template = 'fisheriescape/index.html'

    @tag("fisheriescape", 'index', "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url)

# Not used anymore
# class TestMapView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('fisheriescape:map_view')
#         self.expected_template = 'fisheriescape/map.html'
#
#     @tag("fisheriescape", "map", "view")
#     def test_view_class(self):
#         self.assert_inheritance(views.MapView, TemplateView)
#         self.assert_inheritance(views.MapView, views.FisheriescapeAccessRequired)
#
#     @tag("fisheriescape", 'index', "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url)


class TestScoreMapView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ScoreFactory()
        self.test_url = reverse_lazy('fisheriescape:score_map')
        self.expected_template = 'fisheriescape/search_map.html'
        self.user = self.get_and_login_user()

    @tag("ScoreMap", "score_map", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ScoreMapView, CommonTemplateView)
        self.assert_inheritance(views.ScoreMapView, views.FisheriescapeAccessRequired)

    @tag("ScoreMap", "score_map", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ScoreMap", "score_map", "context")
    def test_context(self):
        context_vars = [
            "field_list",
            "lobster_areas",
            "mapbox_api_key",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("ScoreMap", "score_map", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("fisheriescape:score_map", f"/en/fisheriescape/scores-map/")

