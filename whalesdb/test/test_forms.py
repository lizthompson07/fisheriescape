from django.test import tag
from faker import Factory

from whalesdb.test.common_views import CommonFormTest
from whalesdb import forms
from whalesdb import models

import json

import whalesdb.test.WhalesdbFactory as factory

# location of the fixture files to load, which are also used to create valid_data for testing.
prj_data = 'whalesdb/test/data/prj_fixture.json'
stn_data = 'whalesdb/test/data/stn_fixture.json'
mor_data = 'whalesdb/test/data/mor_fixture.json'
dep_data = 'whalesdb/test/data/dep_fixture.json'
ste_data = 'whalesdb/test/data/ste_fixture.json'
set_data = 'whalesdb/test/data/set_fixture.json'
shared_model_data = 'whalesdb/test/data/shared_model_fixture.json'

# used to create fake data
faker = Factory.create()


class TestDepForm(CommonFormTest):

    def setUp(self) -> None:
        super().setUp()
        self.form_class = forms.DepForm
        self.test_factory = factory.DepFactory

    @tag('dep', 'form', 'valid')
    def test_dep_valid_data(self):
        self.assert_valid_data()

    # test that the project field exists and that it has a "create_url" attribute
    @tag('dep', 'form', 'field')
    def test_dep_prj_field_create(self):
        form = self.form_class()
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
        form = self.form_class()
        self.assertTrue(hasattr(form, 'min_height'))
        self.assertTrue(hasattr(form, 'min_width'))


class TestEqpForm(CommonFormTest):

    @staticmethod
    def get_valid_data():
        valid_data = {
        }

        return valid_data

    def setUp(self) -> None:
        super().setUp()
        self.form_class = forms.EqpForm

    @tag('eqp', 'form', 'valid')
    def test_eqp_valid_data(self):
        self.assert_valid_data()

    # The deployment form should have a minimum height and width used to resize popup windows
    @tag('eqp', 'form', 'properties')
    def test_eqp_properties(self):
        form = self.form_class()
        self.assertTrue(hasattr(form, 'min_height'))
        self.assertTrue(hasattr(form, 'min_width'))


class TestMorForm(CommonFormTest):

    def setUp(self) -> None:
        super().setUp()
        self.form_class = forms.MorForm
        self.test_factory = factory.MorFactory

    @tag('mor', 'form', 'valid')
    def test_mor_valid_data(self):
        self.assert_valid_data()

    # The MooringSetup form should have a minimum height and width used to resize popup windows
    @tag('mor', 'form', 'properties')
    def test_mor_properties(self):
        form = self.form_class()
        self.assertTrue(hasattr(form, 'min_height'))
        self.assertTrue(hasattr(form, 'min_width'))


class TestSteForm(CommonFormTest):

    def setUp(self) -> None:
        super().setUp()
        self.form_class = forms.SteForm
        self.test_factory = factory.SteFactory

    @tag('ste', 'form', 'valid_data')
    def test_ste_valid_data(self):
        self.assert_valid_data()


class TestStnForm(CommonFormTest):

    def setUp(self) -> None:
        super().setUp()
        self.form_class = forms.StnForm
        self.test_factory = factory.StnFactory

    @tag('stn', 'form', 'valid_data')
    def test_stn_valid_data(self):
        self.assert_valid_data()

    # The Station form should have a minimum height and width used to resize popup windows
    @tag('stn', 'form', 'properties')
    def test_stv_properties(self):
        form = self.form_class()
        self.assertTrue(hasattr(form, 'min_height'))
        self.assertTrue(hasattr(form, 'min_width'))


class TestPrjForm(CommonFormTest):

    def setUp(self) -> None:
        super().setUp()
        self.form_class = forms.PrjForm
        self.test_factory = factory.PrjFactory

    @tag('prj', 'form', 'valid_data')
    def test_prj_valid_data(self):
        self.assert_valid_data()
