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


class TestVulnerableSpeciesView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.VulnerableSpeciesFactory()
        self.test_url = reverse_lazy('api:vulnerable-species')
        self.user = self.get_and_login_user()

    @tag("VulnerableSpecies", "vulnerable_species", "view")
    def test_view_class(self):
        self.assert_inheritance(views.VulnerableSpeciesView, ListAPIView)
        self.assert_inheritance(views.VulnerableSpeciesView, views.FisheriescapeAccessRequired)

    @tag("VulnerableSpecies", "vulnerable_species", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)

    @tag("VulnerableSpecies", "vulnerable_species", "correct_url")
    def test_correct_url(self):
        self.assert_correct_url('api:vulnerable-species', f"/api/fisheriescape/vulnerable-species/")

    @tag("VulnerableSpecies", "vulnerable_species", "correct_response")
    def test_correct_response(self):
        response = self.client.get(self.test_url)
        self.assert_dict_has_keys(response.json()[0],["english_name","french_name","latin_name","website"])
