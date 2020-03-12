from django.test import tag
from faker import Factory

from whalesdb.test.common_views import CommonFormTest
from whalesdb import forms

import whalesdb.test.WhalesdbFactory as factory

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

    # test that the required fields exists and that they has a "create_url" attribute
    @tag('dep', 'form', 'field')
    def test_dep_field_create(self):
        form = self.form_class()
        self.assertIn("prj", form.fields)
        self.assertIn("stn", form.fields)
        self.assertIn("mor", form.fields)

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

    def setUp(self) -> None:
        super().setUp()
        self.form_class = forms.EqpForm
        self.test_factory = factory.EqpFactory

    @tag('eqp', 'form', 'valid')
    def test_eqp_valid_data(self):
        self.assert_valid_data()

    # test that the required fields exists and that they has a "create_url" attribute
    @tag('eqp', 'form', 'field')
    def test_dep_field_create(self):
        form = self.form_class()
        self.assertIn("emm", form.fields)
        self.assertIn("eqo_owned_by", form.fields)

        self.assertTrue(hasattr(form.fields['emm'], 'create_url'))
        self.assertEquals(form.fields['emm'].create_url, 'whalesdb:create_emm')

        self.assertTrue(hasattr(form.fields['eqo_owned_by'], 'create_url'))
        self.assertEquals(form.fields['eqo_owned_by'].create_url, 'whalesdb:create_eqo')


class TestEmmForm(CommonFormTest):

    def setUp(self) -> None:
        super().setUp()
        self.form_class = forms.EmmForm
        self.test_factory = factory.EmmFactory

    @tag('mor', 'form', 'valid')
    def test_mor_valid_data(self):
        self.assert_valid_data()

    # The MooringSetup form should have a minimum height and width used to resize popup windows
    @tag('mor', 'form', 'properties')
    def test_mor_properties(self):
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
