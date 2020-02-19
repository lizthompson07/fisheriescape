from django.test import tag
from django.urls import reverse_lazy

from django.core.files.base import ContentFile
from django.utils.six import BytesIO

from PIL import Image

from whalesdb.test.common_views import CommonCreateTest, get_stn, get_prj, get_dep, get_mor

from whalesdb import views, forms

import os


class TestCreateDep(CommonCreateTest):

    img_file_name = None
    img_file_path = None

    data = {
        'dep_year': 2020,
        'dep_month': 2,
        'dep_name': "DEP_001",
    }

    def setUp(self):
        super().setUp()

        stn = get_stn()
        self.data['stn'] = stn.pk

        mor = get_mor()
        self.data['mor'] = mor.pk

        prj = get_prj()
        self.data['prj'] = prj.pk

        self.test_url = reverse_lazy('whalesdb:create_dep')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.CreateDep
        self.expected_form = forms.DepForm

    # Users must be logged in to create new objects
    @tag('dep', 'create_dep', 'response', 'access')
    def test_create_dep_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new objects
    @tag('dep', 'create_dep', 'response', 'access')
    def test_create_dep_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('dep', 'create_dep', 'response', 'access')
    def test_create_dep_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('dep', 'create_dep', 'form')
    def test_create_dep_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('dep', 'create_dep', 'context')
    def test_create_dep_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('dep', 'create_dep', 'redirect')
    def test_create_dep_successful_url(self):
        super().assert_successful_url()


class TestCreateMor(CommonCreateTest):

    img_file_name = None
    img_file_path = None

    data = {
        "mor_name": "MOR_001",
        "mor_max_depth": "10",
        "mor_link_setup_image": "https://somelink.com/images/img001.png",
        "mor_additional_equipment": "None",
        "mor_general_moor_description": "This is a mooring description",
        "more_notes": "Notes",
    }

    def setUp(self):
        super().setUp()

        self.test_url = reverse_lazy('whalesdb:create_mor')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.CreateMor
        self.expected_form = forms.MorForm

        self.img_file_name = "MooringSetupTest.png"
        self.img_file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + self.img_file_name

        data = BytesIO()
        Image.open(self.img_file_path).save(data, "PNG")
        data.seek(0)

        file = ContentFile(data.read(), self.img_file_name)
        # add the image to the data array
        self.data['mor_setup_image'] = self.img_file_path

    # Users must be logged in to create new objects
    @tag('mor', 'create_mor', 'response', 'access')
    def test_create_mor_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new objects
    @tag('mor', 'create_mor', 'response', 'access')
    def test_create_mor_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('mor', 'create_mor', 'response', 'access')
    def test_create_mor_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('mor', 'create_mor', 'form')
    def test_create_mor_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('mor', 'create_mor', 'context')
    def test_create_mor_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('mor', 'create_mor', 'redirect')
    def test_create_mor_successful_url(self):
        super().assert_successful_url()


class TestCreatePrj(CommonCreateTest):
    data = {
        "prj_name": 'PRJ_001',
        "prj_description": "Some project description here",
        "prj_url": "https//noneOfYourBusiness.com"
    }

    def setUp(self):
        super().setUp()

        self.test_url = reverse_lazy('whalesdb:create_prj')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.CreatePrj

        self.expected_form = forms.PrjForm

    # Users must be logged in to create new objects
    @tag('prj', 'create_prj', 'response', 'access')
    def test_create_prj_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new objects
    @tag('prj', 'create_prj', 'response', 'access')
    def test_create_prj_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('prj', 'create_prj', 'response', 'access')
    def test_create_prj_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('prj', 'create_prj', 'form')
    def test_create_prj_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('prj', 'create_prj', 'context')
    def test_create_prj_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('prj', 'create_prj', 'redirect')
    def test_create_prj_successful_url(self):
        super().assert_successful_url()


class TestCreateStn(CommonCreateTest):
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

        self.test_url = reverse_lazy('whalesdb:create_stn')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.CreateStn

        self.expected_form = forms.StnForm

    # Users must be logged in to create new stations
    @tag('stn', 'create_stn', 'response', 'access')
    def test_create_stn_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new stations
    @tag('stn', 'create_stn', 'response', 'access')
    def test_create_stn_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('stn', 'create_stn', 'response', 'access')
    def test_create_stn_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('stn', 'create_stn', 'form')
    def test_create_stn_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('stn', 'create_stn', 'context')
    def test_create_stn_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('stn', 'create_stn', 'redirect')
    def test_create_stn_successful_url(self):
        super().assert_successful_url()
