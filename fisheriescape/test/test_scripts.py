import os

from rest_framework.generics import ListAPIView
from rest_framework.reverse import reverse_lazy
from django.test import tag

from fisheriescape.api import views
from fisheriescape.test import FactoryFloor
from fisheriescape.test.common_tests import CommonFisheriescapeTest as CommonTest
from fisheriescape import scripts
from fisheriescape.models import Score, VulnerableSpeciesSpot

TEST_SCORES_FOLDER = os.path.join(os.path.dirname(__file__), 'test_data','scores')
TEST_VULNERABLE_SPECIES_SPOTS_FOLDER = os.path.join(os.path.dirname(__file__), 'test_data','vulnerable_species_spots')


class TestImportScores(CommonTest):
    def setUp(self):
        super().setUp()

    @tag("Score", "score_import", "import_success")
    def test_import_success(self):
        result = scripts.import_all_scores(folder_path=TEST_SCORES_FOLDER)
        assert not result.get('errors')
        assert Score.objects.count() == 8 # 5 from fixtures and 3 imported by this test


class TestImportVulnerableSpots(CommonTest):
    def setUp(self):
        super().setUp()

    @tag("ScoreFeature", "score_feature", "correct_response")
    def test_import(self):
        result =  scripts.import_all_vulnerable_species_spots(folder_path=TEST_VULNERABLE_SPECIES_SPOTS_FOLDER)
        assert not result.get('errors')
        assert VulnerableSpeciesSpot.objects.count() == 29
