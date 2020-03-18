from django.test import tag
from django.urls import reverse_lazy

from whalesdb.test.common_views import CommonUpdateTest
from whalesdb.test import WhalesdbFactory as Factory

from whalesdb import views, forms


class TestUpdateDep(CommonUpdateTest):

    def setUp(self):
        super().setUp()

        self.data = Factory.DepFactory.get_valid_data()

        obj = Factory.DepFactory()

        self.test_url = reverse_lazy('whalesdb:update_dep', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.DepUpdate

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


class TestUpdateEmm(CommonUpdateTest):

    def setUp(self):
        super().setUp()

        self.data = Factory.EmmFactory.get_valid_data()

        obj = Factory.EmmFactory()

        self.test_url = reverse_lazy('whalesdb:update_emm', args=(obj.pk, 'pop',))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form_no_nav.html'

        self.expected_view = views.EmmUpdate

        self.expected_form = forms.EmmForm

    # Users must be logged in to update stations
    @tag('emm', 'update_emm', 'response', 'access')
    def test_update_emm_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to update stations
    @tag('emm', 'update_emm', 'response', 'access')
    def test_update_emm_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('emm', 'update_emm', 'response', 'access')
    def test_update_emm_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('emm', 'update_emm', 'form')
    def test_update_emm_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('emm', 'update_emm', 'context')
    def test_update_emm_context_fields(self):
        response = super().assert_create_view_context_fields()

    # test that given some valid data the view will redirect to the list
    @tag('emm', 'update_emm', 'redirect')
    def test_update_emm_successful_url(self):
        super().assert_successful_url()


class TestUpdateEqh(CommonUpdateTest):

    def setUp(self):
        super().setUp()

        self.data = Factory.EqhFactory.get_valid_data()

        emm = Factory.EmmFactory(eqt_id=4)
        obj = Factory.EqhFactory(emm=emm)

        self.test_url = reverse_lazy('whalesdb:update_eqh', args=(obj.pk, 'pop',))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form_no_nav.html'

        self.expected_view = views.EqhUpdate

        self.expected_form = forms.EqhForm

    # Users must be logged in to update stations
    @tag('eqh', 'update_eqh', 'response', 'access')
    def test_update_eqh_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to update stations
    @tag('eqh', 'update_eqh', 'response', 'access')
    def test_update_eqh_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('eqh', 'update_eqh', 'response', 'access')
    def test_update_eqh_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('eqh', 'update_eqh', 'form')
    def test_update_eqh_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('eqh', 'update_eqh', 'context')
    def test_update_eqh_context_fields(self):
        response = super().assert_create_view_context_fields()

        # Emm field should NOT be in the update dialog
        self.assertNotIn("emm", response.context)

    # test that given some valid data the view will redirect to the list
    @tag('eqh', 'update_eqh', 'redirect')
    def test_update_eqh_successful_url(self):
        super().assert_successful_url()


class TestUpdateEqr(CommonUpdateTest):

    def setUp(self):
        super().setUp()

        self.data = Factory.EqrFactory.get_valid_data()

        emm = Factory.EmmFactory(eqt_id=1)
        obj = Factory.EqrFactory(emm=emm)

        self.test_url = reverse_lazy('whalesdb:update_eqr', args=(obj.pk, 'pop',))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form_no_nav.html'

        self.expected_view = views.EqrUpdate

        self.expected_form = forms.EqrForm

    # Users must be logged in to update stations
    @tag('eqr', 'update_eqr', 'response', 'access')
    def test_update_eqr_en(self):
        super().assert_view(expected_code=302)

    # Users must be logged in to update stations
    @tag('eqr', 'update_eqr', 'response', 'access')
    def test_update_eqr_fr(self):
        super().assert_view(lang='fr', expected_code=302)

    # Logged in user in the whalesdb_admin group should get to the _entry_form.html template
    @tag('eqr', 'update_eqr', 'response', 'access')
    def test_update_eqr_en_access(self):
        # ensure a user not in the whalesdb_admin group cannot access creation forms
        super().assert_logged_in_not_access()

        # ensure a user in the whales_db_admin group can access creation forms
        super().assert_logged_in_has_access()

    # Test that projects is using the project form
    @tag('eqr', 'update_eqr', 'form')
    def test_update_eqr_form(self):
        super().assert_create_form()

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    @tag('eqr', 'update_eqr', 'context')
    def test_update_eqr_context_fields(self):
        response = super().assert_create_view_context_fields()

        # Emm field should NOT be in the update dialog
        self.assertNotIn("emm", response.context)

    # test that given some valid data the view will redirect to the list
    @tag('eqr', 'update_eqr', 'redirect')
    def test_update_eqr_successful_url(self):
        super().assert_successful_url()


class TestUpdateMor(CommonUpdateTest):

    def setUp(self):
        super().setUp()

        self.data = Factory.MorFactory.get_valid_data()

        obj = Factory.MorFactory()

        self.test_url = reverse_lazy('whalesdb:update_mor', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.MorUpdate

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

    def setUp(self):
        super().setUp()

        self.data = Factory.PrjFactory.get_valid_data()

        obj = Factory.PrjFactory()

        self.test_url = reverse_lazy('whalesdb:update_prj', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.PrjUpdate

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

    def setUp(self):
        super().setUp()

        self.data = Factory.StnFactory.get_valid_data()

        obj = Factory.StnFactory()

        self.test_url = reverse_lazy('whalesdb:update_stn', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_entry_form.html'

        self.expected_view = views.StnUpdate

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
