from django.test import tag
from django.urls import reverse

from whalesdb.test.common_views import CommonFormTest, get_stn, get_prj, get_mor, get_dep
from whalesdb import forms, models


class TestDepForm(CommonFormTest):

    @staticmethod
    def get_valid_data():

        stn = get_stn()
        mor = get_mor()
        prj = get_prj()

        valid_data = {
            'dep_year': 2020,
            'dep_month': 2,
            'dep_name': "DEP_001",
            'stn': stn.pk,
            'mor': mor.pk,
            'prj': prj.pk
        }

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


class TestMorForm(CommonFormTest):

    @staticmethod
    def get_valid_data():

        valid_data = {
            "mor_name": "MOR_001",
            "mor_max_depth": "10",
            "mor_link_setup_image": "https://somelink.com/images/img001.png",
            "mor_additional_equipment": "None",
            "mor_general_moor_description": "This is a mooring description",
            "more_notes": "Notes",
        }

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
        valid_data = {
            "stn_name": "STN_001",
            "stn_code": "STN",
            "stn_revision": "1",
            "stn_planned_lat": "25",
            "stn_planned_lon": "50",
            "stn_planned_depth": "10",
            "stn_notes": "Some Notes"
        }

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
        valid_data = {
            "prj_name": 'PRJ_001',
            "prj_description": "Some project description here",
            "prj_url": "https//noneOfYourBusiness.com"
        }

        return valid_data

    @tag('prj', 'form', 'valid_data')
    def test_prj_valid_data(self):
        form = forms.PrjForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)
