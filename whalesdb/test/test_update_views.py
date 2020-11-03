from django.test import tag, RequestFactory
from django.urls import reverse_lazy
from django.test import TestCase

from whalesdb.test.common_views import CommonUpdateTest, setup_view
from whalesdb.test import WhalesdbFactoryFloor as Factory
from shared_models.test import SharedModelsFactoryFloor as SharedFactory

from whalesdb import views, forms, models


@tag('Cru', 'create')
class TestCruUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = SharedFactory.CruiseFactory.get_valid_data()

        obj = SharedFactory.CruiseFactory()

        self.test_url = reverse_lazy('whalesdb:update_cru', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.CruUpdate

        self.expected_form = forms.CruForm

        self.expected_success_url = reverse_lazy("whalesdb:details_cru", args=(obj.pk,))


@tag('dep', 'update')
class TestDepUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.DepFactory.get_valid_data()

        obj = Factory.DepFactory()

        self.test_url = reverse_lazy('whalesdb:update_dep', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.DepUpdate

        self.expected_form = forms.DepForm

        self.expected_success_url = reverse_lazy("whalesdb:list_dep")

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    def test_update_dep_context_fields(self):
        response = super().get_context()

        # Deploymnets also need to return a JSON formatted list of Station Codes
        self.assertIn("station_json", response.context)
        self.assertIn("java_script", response.context)
        self.assertEquals("whalesdb/_entry_dep_js.html", response.context['java_script'])

    # If a deployment event has been issued, a deployment should no longer be editable and the
    # test_func method should return false. This is to prevent URL hijacking and letting a user
    # paste in data to a url to update a view
    def test_update_dep_test_func_denied(self):
        dep = Factory.DepFactory()

        self.login_whale_user()
        response = self.client.get(reverse_lazy('whalesdb:update_dep', args=(dep.pk,)))

        self.assertTrue(response.context['editable'])

        # create a deployment event
        set_type = models.SetStationEventCode.objects.get(pk=1)  # 1 == Deployment event
        dep_evt = Factory.SteFactory(dep=dep, set_type=set_type)

        response = self.client.get(reverse_lazy('whalesdb:update_dep', args=(dep.pk,)))

        # deployment should no longer be editable
        self.assertFalse(response.context['editable'])


@tag('eca', 'create')
class TestEcaUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.EcaFactory.get_valid_data()

        obj = Factory.EcaFactory()

        self.test_url = reverse_lazy('whalesdb:update_eca', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.EmmUpdate

        self.expected_form = forms.EmmForm

        self.expected_success_url = reverse_lazy("whalesdb:details_eca", args=(obj.pk,))


@tag('emm', 'create')
class TestEmmUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.EmmFactory.get_valid_data()

        obj = Factory.EmmFactory()

        self.test_url = reverse_lazy('whalesdb:update_emm', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.EmmUpdate

        self.expected_form = forms.EmmForm

        self.expected_success_url = reverse_lazy("whalesdb:list_emm")


@tag('eqh', 'create')
class TestEqhUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.EqhFactory.get_valid_data()

        emm = Factory.EmmFactory(pk=4)
        obj = Factory.EqhFactory(emm=emm)

        self.test_url = reverse_lazy('whalesdb:update_eqh', args=(obj.pk, 'pop',))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.EqhUpdate

        self.expected_form = forms.EqhForm

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    def test_update_eqh_context_fields(self):
        response = super().get_context()

        # Emm field should NOT be in the update dialog
        self.assertNotIn("emm", response.context)


@tag('eqp', 'create')
class TestEqpUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.EqpFactory.get_valid_data()

        emm = Factory.EmmFactory()
        obj = Factory.EqpFactory(emm=emm)

        self.test_url = reverse_lazy('whalesdb:update_eqp', args=(obj.pk, 'pop',))

        # Since this is intended to be used as a pop-out form, use the no nav entry form
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.EqpUpdate

        self.expected_form = forms.EqpForm

        self.expected_success_url = reverse_lazy("whalesdb:list_eqp")


@tag('eqr', 'create')
class TestEqrUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.EqrFactory.get_valid_data()

        obj = Factory.EqrFactory()

        self.test_url = reverse_lazy('whalesdb:update_eqr', args=(obj.pk, 'pop',))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.EqrUpdate

        self.expected_form = forms.EqrForm

    # test that the context is returning the required context fields
    # at a minimum this should include a title field
    # Each view might require specific context fields
    def test_update_eqr_context_fields(self):
        response = super().get_context()

        # Emm field should NOT be in the update dialog
        self.assertNotIn("emm", response.context)


@tag('etr', 'create')
class TestEtrUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.EtrFactory.get_valid_data()

        obj = Factory.EtrFactory()

        self.test_url = reverse_lazy('whalesdb:update_etr', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.EtrUpdate

        self.expected_form = forms.EtrForm

        self.expected_success_url = reverse_lazy('whalesdb:details_etr', args=(obj.pk,))


@tag('mor', 'create')
class TestMorUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.MorFactory.get_valid_data()

        obj = Factory.MorFactory()

        self.test_url = reverse_lazy('whalesdb:update_mor', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.MorUpdate

        self.expected_form = forms.MorForm

        self.expected_success_url = reverse_lazy("whalesdb:list_mor")


@tag('prj', 'create')
class TestPrjUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.PrjFactory.get_valid_data()

        obj = Factory.PrjFactory()

        self.test_url = reverse_lazy('whalesdb:update_prj', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.PrjUpdate

        self.expected_form = forms.PrjForm

        self.expected_success_url = reverse_lazy("whalesdb:list_prj")


@tag('ste', 'create')
class TestSteUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.SteFactory.get_valid_data()

        obj = Factory.SteFactory()

        self.data['dep'] = obj.dep_id

        self.test_url = reverse_lazy('whalesdb:update_ste', args=(obj.pk, 'pop',))

        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.SteUpdate

        self.expected_form = forms.SteForm

        self.expected_success_url = reverse_lazy("shared_models:close_me_no_refresh")


@tag('stn', 'create')
class TestStnUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.StnFactory.get_valid_data()

        obj = Factory.StnFactory()

        self.test_url = reverse_lazy('whalesdb:update_stn', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.StnUpdate

        self.expected_form = forms.StnForm
        
        self.expected_success_url = reverse_lazy("whalesdb:list_stn")


@tag('rec', 'create')
class TestRecUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.RecFactory.get_valid_data()

        obj = Factory.RecFactory()

        self.test_url = reverse_lazy('whalesdb:update_rec', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.RecUpdate

        self.expected_form = forms.RecForm

        self.expected_success_url = reverse_lazy("whalesdb:details_rec", args=(obj.pk,))


@tag('ret', 'update')
class TestRetUpdate(CommonUpdateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = Factory.RetFactory.get_valid_data()

        obj = Factory.RetFactory()

        self.test_url = reverse_lazy('whalesdb:update_ret', args=(obj.pk,))

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_view = views.RetUpdate

        self.expected_form = forms.RetForm

        self.expected_success_url = reverse_lazy("whalesdb:list_ret")
