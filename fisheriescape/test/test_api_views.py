from rest_framework.generics import ListAPIView
from rest_framework.reverse import reverse_lazy
from django.test import tag

from fisheriescape.api import views
from fisheriescape.test import FactoryFloor
from fisheriescape.test.common_tests import CommonFisheriescapeTest as CommonTest


class TestScoreFeatureView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ScoreFactory()
        self.test_url = reverse_lazy('api:scores-feature')
        self.user = self.get_and_login_user()

    @tag("ScoreFeature", "score_feature", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ScoreFeatureView, ListAPIView)
        self.assert_inheritance(views.ScoreFeatureView, views.FisheriescapeAccessRequired)

    @tag("ScoreFeature", "score_feature", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)

    @tag("ScoreFeature", "score_feature", "correct_url")
    def test_correct_url(self):
        self.assert_correct_url('api:scores-feature', f"/api/fisheriescape/scores-feature/")

    @tag("ScoreFeature", "score_feature", "correct_response")
    def test_correct_response(self):
        response = self.client.get(self.test_url)
        self.assert_dict_has_keys(response.json(),["type","max_fs_score","features"])

