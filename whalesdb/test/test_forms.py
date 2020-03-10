from django.test import tag
from django.urls import reverse

from whalesdb.test.common_views import CommonFormTest, get_stn, get_prj, get_mor, get_dep
from whalesdb import forms, models

import json


# location of the fixture files to load, which are also used to create valid_data for testing.
prj_data = 'whalesdb/test/data/prj_fixture.json'
stn_data = 'whalesdb/test/data/stn_fixture.json'
mor_data = 'whalesdb/test/data/mor_fixture.json'
dep_data = 'whalesdb/test/data/dep_fixture.json'


# TODO: Create fixtures for loading dependencies in the 'get_valid_data()' methods in all form test classes
class TestDepForm(CommonFormTest):

    @staticmethod
    def get_valid_data():

        # make sure fixtures are loaded in calling class
        # fixtures = [test_forms.mor_data, test_forms.prj_data, test_forms.stn_data]
        valid_data = {}
        with open(dep_data) as json_file:
            data = json.load(json_file)
            valid_data = data[3]['fields']

        return valid_data

    @tag('dep', 'form', 'valid')
    def test_dep_valid_data(self):
        form = forms.DepForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)

    # test that the project field exists and that it has a "create_url" attribute
    @tag('dep', 'form', 'field')
    def test_dep_prj_field_create(self):
        form = forms.DepForm()
        self.assertIn("prj", form.fields)
        self.assertTrue(hasattr(form.fields['stn'], 'create_url'))
        self.assertEquals(form.fields['stn'].create_url, 'whalesdb:create_stn')

        self.assertTrue(hasattr(form.fields['prj'], 'create_url'))
        self.assertEquals(form.fields['prj'].create_url, 'whalesdb:create_prj')

        self.assertTrue(hasattr(form.fields['mor'], 'create_url'))
        self.assertEquals(form.fields['mor'].create_url, 'whalesdb:create_mor')

    # The deployment form should have a minimum height and width used to resize popup windows
    @tag('dep', 'form', 'properties')
    def test_dep_properties(self):
        form = forms.DepForm()
        self.assertTrue(hasattr(form, 'min_height'))
        self.assertTrue(hasattr(form, 'min_width'))


class TestEqpForm(CommonFormTest):

    @staticmethod
    def get_valid_data():
        valid_data = {
        }

        return valid_data

    # TODO: Create a fixture for loading equipment dependencies
    @tag('eqp', 'form', 'valid')
    def test_eqp_valid_data(self):
        form = forms.EqpForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)

    # The deployment form should have a minimum height and width used to resize popup windows
    @tag('eqp', 'form', 'properties')
    def test_eqp_properties(self):
        form = forms.DepForm()
        self.assertTrue(hasattr(form, 'min_height'))
        self.assertTrue(hasattr(form, 'min_width'))


class TestMorForm(CommonFormTest):

    @staticmethod
    def get_valid_data():
        valid_data = {}
        with open(mor_data) as json_file:
            data = json.load(json_file)
            valid_data = data[0]['fields']

        return valid_data

    @tag('mor', 'form', 'valid')
    def test_mor_valid_data(self):
        form = forms.MorForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)

    # The MooringSetup form should have a minimum height and width used to resize popup windows
    @tag('mor', 'form', 'properties')
    def test_mor_properties(self):
        form = forms.MorForm()
        self.assertTrue(hasattr(form, 'min_height'))
        self.assertTrue(hasattr(form, 'min_width'))


class TestSteForm(CommonFormTest):

    @staticmethod
    def get_valid_data():
        dep = get_dep()

        valid_data = {
            'dep': dep.pk,
            'set_type': 1,
            'ste_date': '2020-02-01',
            'crs': 1
        }

        return valid_data

    @tag('ste', 'form', 'valid_data')
    def test_ste_valid_data(self):
        form = forms.SteForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)


class TestStnForm(CommonFormTest):

    @staticmethod
    def get_valid_data():
        valid_data = {}
        with open(stn_data) as json_file:
            data = json.load(json_file)
            valid_data = data[0]['fields']

        return valid_data

    @tag('stn', 'form', 'valid_data')
    def test_stn_valid_data(self):
        form = forms.StnForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)

    # The Station form should have a minimum height and width used to resize popup windows
    @tag('stn', 'form', 'properties')
    def test_stv_properties(self):
        form = forms.StnForm()
        self.assertTrue(hasattr(form, 'min_height'))
        self.assertTrue(hasattr(form, 'min_width'))


class TestPrjForm(CommonFormTest):

    @staticmethod
    def get_valid_data():
        valid_data = {}
        with open(prj_data) as json_file:
            data = json.load(json_file)
            valid_data = data[0]['fields']

        return valid_data

    @tag('prj', 'form', 'valid_data')
    def test_prj_valid_data(self):
        form = forms.PrjForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)
