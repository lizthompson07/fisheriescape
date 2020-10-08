from django.urls import reverse_lazy
from django.test import tag, TestCase

from whalesdb.test.common_views import CommonDetailsTest
from whalesdb.test import WhalesdbFactoryFloor as Factory
from shared_models.test import SharedModelsFactoryFloor as SharedFactory


@tag('cru', 'detail')
class TestCruDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        obj = SharedFactory.CruiseFactory()

        self._details_dict['cru_1'] = obj

        return self._details_dict

    def setUp(self):
        super().setUp()

        cru_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_cru', args=(cru_dic['cru_1'].pk,))
        self.test_expected_template = 'whalesdb/whales_details.html'
        self.fields = []


@tag('dep', 'detail')
class TestDepDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        # There should be one dep object loaded from the fixtures
        dep_1 = Factory.DepFactory()

        self._details_dict['dep_1'] = dep_1

        return self._details_dict

    def setUp(self):
        super().setUp()

        dep_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_dep', args=(dep_dic['dep_1'].pk,))
        self.test_expected_template = 'whalesdb/details_dep.html'
        self.fields = ['dep_year', 'dep_month', 'dep_name', 'stn', 'prj', 'mor']

    # Test that the context contains the proper fields
    def test_context_fields_dep(self):
        response = super().get_context()

        # Google API key is required so map of station location doesn't nag about being in dev mode
        self.assertIn("google_api_key", response.context)
        self.assertEqual(response.context['list_url'], 'whalesdb:list_dep')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_dep')

        self.assertEqual(response.context["object"], self.createDict()['dep_1'])
        super().assert_field_in_fields(response)

        # Test that the context contains the proper fields

        # If there is a Dataset associated with the deployment it should be passed as a context variable to the
    # Deployment details page so it can be linked to.
    def test_context_fields_dep_w_rec(self):
        rec = Factory.RecFactory()
        dep = rec.eda_id.dep
        test_url = reverse_lazy('whalesdb:details_dep', args=(dep.pk,))

        response = super().get_context(url=test_url)

        self.assertIsNotNone(response.context['rec'])
        self.assertEqual(str(rec), response.context['rec'][0]['text'])
        self.assertEqual(rec.id, response.context['rec'][0]['id'])


@tag('eca', 'detail')
class TestEcaDetails(CommonDetailsTest, TestCase):

    def setUp(self):
        super().setUp()

        self.eca = Factory.EcaFactory()

        self.test_url = reverse_lazy('whalesdb:details_eca', args=(self.eca.pk,))
        self.test_expected_template = 'whalesdb/details_eca.html'
        self.fields = []


@tag('emm', 'detail')
class TestEmmDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        obj = Factory.EmmFactory()

        self._details_dict['emm_1'] = obj

        return self._details_dict

    def setUp(self):
        super().setUp()

        emm_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_emm', args=(emm_dic['emm_1'].pk,))
        self.test_expected_template = 'whalesdb/details_emm.html'
        self.fields = []


@tag('eqp', 'detail')
class TestEqpDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        obj = Factory.EqpFactory()

        self._details_dict['eqp_1'] = obj

        return self._details_dict

    def setUp(self):
        super().setUp()

        eqp_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_eqp', args=(eqp_dic['eqp_1'].pk,))
        self.test_expected_template = 'whalesdb/details_eqp.html'
        self.fields = []


@tag('er', 'detail')
class TestEtrDetails(CommonDetailsTest, TestCase):

    def setUp(self):
        super().setUp()

        self.etr = Factory.EtrFactory()

        self.test_url = reverse_lazy('whalesdb:details_etr', args=(self.etr.pk,))
        self.test_expected_template = 'whalesdb/whales_details.html'
        self.fields = ['eqp', 'etr_date', 'etr_issue_desc', 'etr_repair_desc', 'etr_repaired_by', 'etr_dep_affe',
                       'etr_rec_affe']

    # Test that the context contains the proper fields
    def test_context_fields_etr(self):
        response = super().get_context()

        self.assertEqual(response.context['list_url'], 'whalesdb:list_etr')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_etr')

        self.assertEqual(response.context["object"], self.etr)
        super().assert_field_in_fields(response)


@tag('mor', 'detail')
class TestMorDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        # There should be one mooring setup loaded from the fixtures
        mor_1 = Factory.MorFactory()

        self._details_dict['mor_1'] = mor_1

        return self._details_dict

    def setUp(self):
        super().setUp()

        mor_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_mor', args=(mor_dic['mor_1'].pk,))
        self.test_expected_template = 'whalesdb/details_mor.html'
        self.fields = ['mor_name', 'mor_max_depth', 'mor_link_setup_image', 'mor_additional_equipment',
                       'mor_general_moor_description', 'mor_notes']

    # Test that the context contains the proper fields
    def test_context_fields_mor(self):
        response = super().get_context()

        self.assertEqual(response.context['list_url'], 'whalesdb:list_mor')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_mor')

        self.assertEqual(response.context["object"], self.createDict()['mor_1'])
        super().assert_field_in_fields(response)


@tag('prj', 'detail')
class TestPrjDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        prj_1 = Factory.PrjFactory()

        self._details_dict['prj_1'] = prj_1

        return self._details_dict

    def setUp(self):
        super().setUp()

        stn_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_prj', args=(stn_dic['prj_1'].pk,))
        self.test_expected_template = 'whalesdb/whales_details.html'

    # Test that the context contains the proper fields
    def test_context_fields_prj(self):
        response = super().get_context()

        self.assertEqual(response.context['list_url'], 'whalesdb:list_prj')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_prj')

        self.assertEqual(response.context['object'], self.createDict()['prj_1'])
        super().assert_field_in_fields(response)


@tag('rec', 'detail')
class TestRecDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        rec_1 = Factory.RecFactory()

        self._details_dict['rec_1'] = rec_1

        return self._details_dict

    def setUp(self):
        super().setUp()

        stn_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_rec', args=(stn_dic['rec_1'].pk,))
        self.test_expected_template = 'whalesdb/details_rec.html'

    # Test that the context contains the proper fields
    def test_context_fields_rec(self):
        response = super().get_context(whale_user=False)

        self.assertEqual(response.context['list_url'], 'whalesdb:list_rec')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_rec')

        self.assertEqual(response.context['object'], self.createDict()['rec_1'])
        self.assertFalse(response.context['editable'])
        super().assert_field_in_fields(response)

    # Test that an rec object isn't editable even if the user is logged in with rights
    def test_context_fields_auth_rec(self):
        response = super().get_context()

        self.assertTrue(response.context['auth'])
        self.assertTrue(response.context['editable'])


@tag('rsc', 'detail')
class TestRscDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        rsc_1 = Factory.RscFactory()

        self._details_dict['rsc_1'] = rsc_1

        return self._details_dict

    def setUp(self):
        super().setUp()

        stn_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_rsc', args=(stn_dic['rsc_1'].pk,))
        self.test_expected_template = 'whalesdb/details_rsc.html'

    # Test that the context contains the proper fields
    def test_context_fields_rsc(self):
        response = super().get_context()
        
        self.assertEqual(response.context['list_url'], 'whalesdb:list_rsc')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_rsc')

        self.assertEqual(response.context['object'], self.createDict()['rsc_1'])
        self.assertFalse(response.context['editable'])
        super().assert_field_in_fields(response)

    # Test that an rsc object isn't editable even if the user is logged in with rights
    def test_context_fields_auth_rsc(self):
        response = super().get_context()

        self.assertTrue(response.context['auth'])
        self.assertFalse(response.context['editable'])


@tag('stn', 'detail')
class TestStnDetails(CommonDetailsTest, TestCase):

    def createDict(self):
        if self._details_dict:
            return self._details_dict

        self._details_dict = {}

        # Should be one station loaded from the fixtures
        stn_1 = Factory.StnFactory()

        self._details_dict['stn_1'] = stn_1

        return self._details_dict

    def setUp(self):
        super().setUp()

        stn_dic = self.createDict()

        self.test_url = reverse_lazy('whalesdb:details_stn', args=(stn_dic['stn_1'].pk,))
        self.test_expected_template = 'whalesdb/details_stn.html'
        self.fields = ['stn_name', 'stn_code', 'stn_revision', 'stn_planned_lat', 'stn_planned_lon',
                       'stn_planned_depth', 'stn_notes']

    # Test that the context contains the proper fields
    
    def test_context_fields_stn(self):
        response = super().get_context()

        # Google API key is required so map of station location doesn't nag about being in dev mode
        self.assertIn("google_api_key", response.context)
        self.assertEqual(response.context['list_url'], 'whalesdb:list_stn')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_stn')
        self.assertEqual(response.context['object'], self.createDict()['stn_1'])

        super().assert_field_in_fields(response)
