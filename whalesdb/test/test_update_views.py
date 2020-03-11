from django.test import tag
from django.urls import reverse_lazy

from whalesdb.test.common_views import CommonUpdateTest
from whalesdb.test import test_forms

from whalesdb import views, models, forms


class TestUpdateDep(CommonUpdateTest):

    fixtures = [test_forms.mor_data, test_forms.prj_data, test_forms.stn_data]

    def setUp(self):
        super().setUp()

        self.data = test_forms.TestDepForm.get_valid_data()

        obj = models.DepDeployment(
            dep_year=self.data['dep_year'],
            dep_month=self.data['dep_month'],
            dep_name=self.data['dep_name'],
            stn=models.StnStation.objects.get(pk=self.data['stn']),
            prj=models.PrjProject.objects.get(pk=self.data['prj']),
            mor=models.MorMooringSetup.objects.get(pk=self.data['mor']),
        )
        obj.save()

        self.test_url = reverse_lazy('whalesdb:update_dep', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.UpdateDep

        self.expected_form = forms.DepForm

    # Users must be logged in to update stations
    @tag('dep', 'update_dep', 'response', 'access')
    def test_update_dep_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to update stations
    @tag('dep', 'update_dep', 'response', 'access')
    def test_update_dep_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('dep', 'update_dep', 'response', 'access')
    def test_update_dep_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('dep', 'update_dep', 'form')
    def test_update_dep_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('dep', 'update_dep', 'context')
    def test_update_dep_context_fields(self):
        response = super().assert_create_view_context_fields()

        # Deploymnets also need to return a JSON formatted list of Station Codes
        self.assertIn("station_json", response.context)

    # test that given some valid data the view will redirect to the list
    @tag('dep', 'update_dep', 'redirect')
    def test_update_dep_successful_url(self):
        super().assert_successful_url()


class TestUpdateMor(CommonUpdateTest):
    data = {
        "mor_name": "MOR_001",
        "mor_max_depth": "10",
        "mor_link_setup_image": "https://somelink.com/images/img001.png",
        "mor_additional_equipment": "None",
        "mor_general_moor_description": "This is a mooring description",
        "mor_notes": "Notes",
    }

    def setUp(self):
        super().setUp()

        obj = models.MorMooringSetup(
            mor_name=self.data['mor_name'],
            mor_max_depth=self.data['mor_max_depth'],
            mor_link_setup_image=self.data['mor_link_setup_image'],
            mor_additional_equipment=self.data['mor_additional_equipment'],
            mor_general_moor_description=self.data['mor_general_moor_description'],
            mor_notes=self.data['mor_notes'],
        )
        obj.save()

        self.test_url = reverse_lazy('whalesdb:update_mor', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.UpdateMor

        self.expected_form = forms.MorForm

    # Users must be logged in to update stations
    @tag('mor', 'update_mor', 'response', 'access')
    def test_update_mor_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to update stations
    @tag('mor', 'update_mor', 'response', 'access')
    def test_update_mor_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('mor', 'update_mor', 'response', 'access')
    def test_update_mor_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('mor', 'update_mor', 'form')
    def test_update_mor_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('mor', 'update_mor', 'context')
    def test_update_mor_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('mor', 'update_mor', 'redirect')
    def test_update_mor_successful_url(self):
        super().assert_successful_url()


class TestUpdatePrj(CommonUpdateTest):
    data = {
        "prj_name": 'PRJ_001',
        "prj_description": "Some project description here",
        "prj_url": "https//noneOfYourBusiness.com"
    }

    def setUp(self):
        super().setUp()

        obj = models.PrjProject(
            prj_name=self.data['prj_name'],
            prj_description=self.data['prj_description'],
            prj_url=self.data['prj_url'],
        )
        obj.save()

        self.test_url = reverse_lazy('whalesdb:update_prj', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.UpdatePrj

        self.expected_form = forms.PrjForm

    # Users must be logged in to create new stations
    @tag('prj', 'update_prj', 'response', 'access')
    def test_update_prj_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to update stations
    @tag('prj', 'update_prj', 'response', 'access')
    def test_update_prj_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('prj', 'update_prj', 'response', 'access')
    def test_update_prj_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('prj', 'update_prj', 'form')
    def test_update_prj_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('prj', 'update_prj', 'context')
    def test_update_prj_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('prj', 'update_prj', 'redirect')
    def test_update_prj_successful_url(self):
        super().assert_successful_url()


class TestUpdateStn(CommonUpdateTest):
    data = {
        "stn_name": "STN_001",
        "stn_code": "STN",
        "stn_revision": "1",
        "stn_planned_lat": "25",
        "stn_planned_lon": "50",
        "stn_planned_depth": "10",
        "stn_notes": "Some Notes"
    }

    def setUp(self):
        super().setUp()

        obj = models.StnStation(
            stn_name=self.data['stn_name'],
            stn_code=self.data['stn_code'],
            stn_revision=self.data['stn_revision'],
            stn_planned_lat=self.data['stn_planned_lat'],
            stn_planned_lon=self.data['stn_planned_lon'],
            stn_planned_depth=self.data['stn_planned_depth'],
            stn_notes=self.data['stn_notes']
        )
        obj.save()

        self.test_url = reverse_lazy('whalesdb:update_stn', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.UpdateStn

        self.expected_form = forms.StnForm

    # Users must be logged in to create new stations
    @tag('stn', 'update_stn', 'response', 'access')
    def test_update_stn_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to update stations
    @tag('stn', 'update_stn', 'response', 'access')
    def test_update_stn_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('stn', 'update_stn', 'response', 'access')
    def test_update_stn_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('stn', 'update_stn', 'form')
    def test_update_stn_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('stn', 'update_stn', 'context')
    def test_update_stn_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('stn', 'update_stn', 'redirect')
    def test_update_stn_successful_url(self):
        super().assert_successful_url()
