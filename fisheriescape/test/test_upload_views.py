import os

from django.core.files.base import ContentFile
from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import FormView

from fisheriescape import views
from fisheriescape.test.common_tests import CommonFisheriescapeTest as CommonTest

TEST_VULNERABLE_SPECIES_SPOTS_DATA_PATH = os.path.join(os.path.dirname(__file__), 'test_data',
                                                       'vulnerable_species_spots', 'vulnerable_spots.csv')

TEST_FISHERIES_SCORES_DATA_PATH = os.path.join(os.path.dirname(__file__), 'test_data',
                                                       'scores', 'score_data.csv')

class TestVulnerableSpeciesSpotsUploadView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('fisheriescape:import_vulnerable_species_spots')
        self.expected_template = 'fisheriescape/import_vulnerable_species_spots.html'
        self.user = self.get_and_login_user(in_group="fisheriescape_admin")

    @tag("Upload", "import_vulnerable_species_spots", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ImportVulnerableSpeciesSpotsView, FormView)
        self.assert_inheritance(views.ImportVulnerableSpeciesSpotsView, views.FisheriescapeAdminAccessRequired)

    @tag("Upload", "import_vulnerable_species_spots", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Upload", "import_vulnerable_species_spots", "submit")
    def test_submit(self):
        with open(file=TEST_VULNERABLE_SPECIES_SPOTS_DATA_PATH, mode="rb") as file:
            file = ContentFile(content=file.read(), name=os.path.basename(TEST_VULNERABLE_SPECIES_SPOTS_DATA_PATH))
            data = {"file" : file}
            self.assert_success_url(self.test_url, data=data, user=self.user, expected_code=200)

    @tag("Upload", "import_vulnerable_species_spots", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("fisheriescape:import_vulnerable_species_spots",
                                f"/en/fisheriescape/import/vulnerable-species-spots")


class TestFisheriescapeScoresUploadView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('fisheriescape:import_fisheriescape_scores')
        self.expected_template = 'fisheriescape/import_fisheriescape_scores.html'
        self.user = self.get_and_login_user(in_group="fisheriescape_admin")

    @tag("Upload", "import_fisheriescape_scores", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ImportFisheriescapeScoresView, FormView)
        self.assert_inheritance(views.ImportFisheriescapeScoresView, views.FisheriescapeAdminAccessRequired)

    @tag("Upload", "import_fisheriescape_scores", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Upload", "import_fisheriescape_scores", "submit")
    def test_submit(self):
        with open(file=TEST_FISHERIES_SCORES_DATA_PATH, mode="rb") as file:
            file = ContentFile(content=file.read(), name=os.path.basename(TEST_FISHERIES_SCORES_DATA_PATH))
            data = {"file" : file}
            self.assert_success_url(self.test_url, data=data, user=self.user, expected_code=200)

    @tag("Upload", "import_fisheriescape_scores", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("fisheriescape:import_fisheriescape_scores",
                                f"/en/fisheriescape/import/fisheriescape-scores")
