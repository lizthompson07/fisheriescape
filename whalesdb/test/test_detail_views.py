from django.utils.translation import activate
from django.urls import reverse_lazy
from django.test import tag

from whalesdb.test.common_views import CommonDetailsTest
from whalesdb.test import WhalesdbFactory as Factory
from whalesdb import models


class TestDetailsEmm(CommonDetailsTest):

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
        self.test_expected_template = 'whalesdb/emm_details.html'
        self.fields = []

    @tag('emm', 'details_emm', 'response', 'access')
    def test_details_emm_en(self):
        super().assert_view()

    # Station Details are visible to all
    @tag('emm', 'details_emm', 'response', 'access')
    def test_details_emm_fr(self):
        super().assert_view(lang='fr')

    # Test that the context contains the proper fields
    @tag('emm', 'details_emm', 'context')
    def test_context_fields_emm(self):
        activate('en')

        response = self.client.get(self.test_url)

        super().assert_context_fields(response)


class TestDetailsEqp(CommonDetailsTest):

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
        self.test_expected_template = 'whalesdb/whales_details.html'
        self.fields = []

    @tag('eqp', 'details_eqp', 'response', 'access')
    def test_details_eqp_en(self):
        super().assert_view()

    # Station Details are visible to all
    @tag('eqp', 'details_eqp', 'response', 'access')
    def test_details_eqp_fr(self):
        super().assert_view(lang='fr')

    # Test that the context contains the proper fields
    @tag('eqp', 'details_eqp', 'context')
    def test_context_fields_eqp(self):
        activate('en')

        response = self.client.get(self.test_url)

        super().assert_context_fields(response)


class TestDetailsDeployment(CommonDetailsTest):

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
        self.test_expected_template = 'whalesdb/depdeployment_details.html'
        self.fields = ['dep_year', 'dep_month', 'dep_name', 'stn', 'prj', 'mor']

    # Station Details are visible to all
    @tag('dep', 'details_dep', 'response', 'access')
    def test_details_dep_en(self):
        super().assert_view()

    # Station Details are visible to all
    @tag('dep', 'details_dep', 'response', 'access')
    def test_details_dep_fr(self):
        super().assert_view(lang='fr')

    # Test that the context contains the proper fields
    @tag('dep', 'details_dep', 'context')
    def test_context_fields_dep(self):
        activate('en')

        response = self.client.get(self.test_url)

        super().assert_context_fields(response)
        # Google API key is required so map of station location doesn't nag about being in dev mode
        self.assertIn("google_api_key", response.context)
        self.assertEqual(response.context['list_url'], 'whalesdb:list_dep')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_dep')

        self.assertEqual(response.context["object"], self.createDict()['dep_1'])
        super().assert_field_in_fields(response)


class TestDetailsMooring(CommonDetailsTest):

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
        self.test_expected_template = 'whalesdb/mormooringsetup_details.html'
        self.fields = ['mor_name', 'mor_max_depth', 'mor_link_setup_image', 'mor_additional_equipment',
                       'mor_general_moor_description', 'mor_notes']

    # Station Details are visible to all
    @tag('mor', 'details_mor', 'response', 'access')
    def test_details_mor_en(self):
        super().assert_view()

    # Station Details are visible to all
    @tag('mor', 'details_mor', 'response', 'access')
    def test_details_mor_fr(self):
        super().assert_view(lang='fr')

    # Test that the context contains the proper fields
    @tag('mor', 'details_mor', 'context')
    def test_context_fields_mor(self):
        activate('en')

        response = self.client.get(self.test_url)

        super().assert_context_fields(response)
        self.assertEqual(response.context['list_url'], 'whalesdb:list_mor')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_mor')

        self.assertEqual(response.context["object"], self.createDict()['mor_1'])
        super().assert_field_in_fields(response)


class TestDetailsProject(CommonDetailsTest):

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

    # Project Details are visible to all
    @tag('prj', 'details_prj', 'response', 'access')
    def test_details_prj_en(self):
        super().assert_view()

    # Project Details are visible to all
    @tag('prj', 'details_prj', 'response', 'access')
    def test_details_prj_fr(self):
        super().assert_view(lang='fr')

    # Test that the context contains the proper fields
    @tag('prj', 'details_prj', 'context')
    def test_context_fields_prj(self):
        activate('en')

        response = self.client.get(self.test_url)

        super().assert_context_fields(response)
        self.assertEqual(response.context['list_url'], 'whalesdb:list_prj')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_prj')

        self.assertEqual(response.context['object'], self.createDict()['prj_1'])
        super().assert_field_in_fields(response)


class TestDetailsStation(CommonDetailsTest):

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
        self.test_expected_template = 'whalesdb/stnstation_details.html'
        self.fields = ['stn_name', 'stn_code', 'stn_revision', 'stn_planned_lat', 'stn_planned_lon',
                       'stn_planned_depth', 'stn_notes']

    # Station Details are visible to all
    @tag('stn', 'details_stn', 'response', 'access')
    def test_details_stn_en(self):
        super().assert_view(expected_template='whalesdb/stnstation_details.html')

    # Station Details are visible to all
    @tag('stn', 'stn', 'details_stn', 'response', 'access')
    def test_details_stn_fr(self):
        super().assert_view(lang='fr', expected_template='whalesdb/stnstation_details.html')

    # Test that the context contains the proper fields
    @tag('stn', 'details_stn', 'context')
    def test_context_fields_stn(self):
        activate('fr')

        response = self.client.get(self.test_url)

        super().assert_context_fields(response)

        # Google API key is required so map of station location doesn't nag about being in dev mode
        self.assertIn("google_api_key", response.context)
        self.assertEqual(response.context['list_url'], 'whalesdb:list_stn')
        self.assertEqual(response.context['update_url'], 'whalesdb:update_stn')
        self.assertEqual(response.context['object'], self.createDict()['stn_1'])
        super().assert_field_in_fields(response)
