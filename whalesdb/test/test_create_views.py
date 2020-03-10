from django.test import tag
from django.urls import reverse_lazy

from django.core.files.base import ContentFile
from django.utils.six import BytesIO

from PIL import Image

from whalesdb.test.common_views import CommonCreateTest, get_stn, get_prj, get_dep, get_mor

from whalesdb import views, forms, models

import os
from whalesdb.test import test_forms


class TestCreateDep(CommonCreateTest):
    fixtures = [test_forms.mor_data, test_forms.prj_data, test_forms.stn_data]

    def setUp(self):
        super().setUp()

        self.data = test_forms.TestDepForm.get_valid_data()

        self.test_url = reverse_lazy('whalesdb:create_dep')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_success_url = reverse_lazy('whalesdb:list_dep')

        self.expected_view = views.CreateDep
        self.expected_form = forms.DepForm

    # Users must be logged in to create new objects
    @tag('dep', 'create', 'response', 'access')
    def test_create_dep_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new objects
    @tag('dep', 'create', 'response', 'access')
    def test_create_dep_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('dep', 'create', 'response', 'access')
    def test_create_dep_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('dep', 'create', 'form')
    def test_create_dep_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('dep', 'create', 'context')
    def test_create_dep_context_fields(self):
        response = super().assert_create_view_context_fields()

        # Deploymnets also need to return a JSON formatted list of Station Codes
        self.assertIn("station_json", response.context)

    # test that given some valid data the view will redirect to the list
    @tag('dep', 'create', 'redirect')
    def test_create_dep_successful_url(self):
        super().assert_successful_url()


class TestCreateEqp(CommonCreateTest):

    def setUp(self):
        super().setUp()

        self.data = test_forms.TestEqpForm.get_valid_data()

        self.test_url = reverse_lazy('whalesdb:create_eqp')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_success_url = reverse_lazy('whalesdb:list_eqp')

        self.expected_view = views.CreateEqp
        self.expected_form = forms.EqpForm

    # Users must be logged in to create new objects
    @tag('eqp', 'create', 'response', 'access')
    def test_create_eqp_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new objects
    @tag('eqp', 'create', 'response', 'access')
    def test_create_eqp_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('eqp', 'create', 'response', 'access')
    def test_create_eqp_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('eqp', 'create', 'form')
    def test_create_eqp_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('eqp', 'create', 'context')
    def test_create_eqp_context_fields(self):
        response = super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('eqp', 'create', 'redirect')
    def test_create_eqp_successful_url(self):
        super().assert_successful_url()


class TestCreateMor(CommonCreateTest):

    img_file_name = None
    img_file_path = None

    def setUp(self):
        super().setUp()
        self.data = test_forms.TestMorForm.get_valid_data()
        self.test_url = reverse_lazy('whalesdb:create_mor')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_success_url = reverse_lazy('whalesdb:list_mor')

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

    def tearDown(self):
        mors = models.MorMooringSetup.objects.all()
        for mor in mors:
            mor.delete()

    # Users must be logged in to create new objects
    @tag('mor', 'create', 'response', 'access')
    def test_create_mor_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new objects
    @tag('mor', 'create', 'response', 'access')
    def test_create_mor_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('mor', 'create', 'response', 'access')
    def test_create_mor_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('mor', 'create', 'form')
    def test_create_mor_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('mor', 'create', 'context')
    def test_create_mor_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('mor', 'create', 'redirect')
    def test_create_mor_successful_url(self):
        super().assert_successful_url()


class TestCreatePrj(CommonCreateTest):

    def setUp(self):
        super().setUp()
        self.data = test_forms.TestPrjForm.get_valid_data()

        self.test_url = reverse_lazy('whalesdb:create_prj')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_success_url = reverse_lazy('whalesdb:list_prj')

        self.expected_view = views.CreatePrj

        self.expected_form = forms.PrjForm

    # Users must be logged in to create new objects
    @tag('prj', 'create', 'response', 'access')
    def test_create_prj_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new objects
    @tag('prj', 'create', 'response', 'access')
    def test_create_prj_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('prj', 'create', 'response', 'access')
    def test_create_prj_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('prj', 'create', 'form')
    def test_create_prj_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('prj', 'create', 'context')
    def test_create_prj_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('prj', 'create', 'redirect')
    def test_create_prj_successful_url(self):
        super().assert_successful_url()


class TestCreateSte(CommonCreateTest):

    def setUp(self):
        super().setUp()

        self.data = test_forms.TestSteForm.get_valid_data()

        self.test_url = reverse_lazy('whalesdb:create_ste', args={self.data['dep']})

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.CreateSte

        self.expected_form = forms.SteForm

    # Users must be logged in to create new stations
    @tag('ste', 'create', 'response', 'access')
    def test_create_ste_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new stations
    @tag('ste', 'create', 'response', 'access')
    def test_create_ste_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('ste', 'create', 'response', 'access')
    def test_create_ste_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('ste', 'create', 'form')
    def test_create_ste_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('ste', 'create', 'context')
    def test_create_ste_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('ste', 'create', 'redirect')
    def test_create_ste_successful_url(self):
        super().assert_successful_url()


class TestCreateStn(CommonCreateTest):
    data = test_forms.TestStnForm.get_valid_data()

    def setUp(self):
        super().setUp()

        self.test_url = reverse_lazy('whalesdb:create_stn')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.CreateStn

        self.expected_form = forms.StnForm

        self.expected_success_url = reverse_lazy('whalesdb:list_stn')

    # Users must be logged in to create new stations
    @tag('stn', 'create', 'response', 'access')
    def test_create_stn_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to create new stations
    @tag('stn', 'create', 'response', 'access')
    def test_create_stn_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('stn', 'create', 'response', 'access')
    def test_create_stn_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('stn', 'create', 'form')
    def test_create_stn_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('stn', 'create', 'context')
    def test_create_stn_context_fields(self):
        super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('stn', 'create', 'redirect')
    def test_create_stn_successful_url(self):
        super().assert_successful_url()
