from django.test import TestCase, tag

from whalesdb.test.common_views import get_stn, get_prj, get_mor
from whalesdb import forms


class TestDepForm(TestCase):

    valid_data = None

    def setUp(self) -> None:
        stn = get_stn()
        mor = get_mor()
        prj = get_prj()

        self.valid_data = {
            'dep_year': 2020,
            'dep_month': 2,
            'dep_name': "DEP_001",
            'stn': stn.pk,
            'mor': mor.pk,
            'prj': prj.pk
        }

    @tag('dep', 'form', 'valid')
    def test_dep_valid_data(self):
        form = forms.DepForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)


class TestMorForm(TestCase):
    valid_data = {
        "mor_name": "MOR_001",
        "mor_max_depth": "10",
        "mor_link_setup_image": "https://somelink.com/images/img001.png",
        "mor_additional_equipment": "None",
        "mor_general_moor_description": "This is a mooring description",
        "more_notes": "Notes",
    }

    @tag('mor', 'form', 'valid')
    def test_mor_valid_data(self):
        form = forms.MorForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)


class TestSteForm(TestCase):
    valid_data = {
        }

    @tag('ste', 'form', 'valid_data')
    def test_ste_valid_data(self):
        form = forms.SteForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)


class TestStnForm(TestCase):
    valid_data = {
            "stn_name": "STN_001",
            "stn_code": "STN",
            "stn_revision": "1",
            "stn_planned_lat": "25",
            "stn_planned_lon": "50",
            "stn_planned_depth": "10",
            "stn_notes": "Some Notes"
        }

    @tag('stn', 'form', 'valid_data')
    def test_stn_valid_data(self):
        form = forms.StnForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)


class TestPrjForm(TestCase):
    valid_data = {
        "prj_name": 'PRJ_001',
        "prj_description": "Some project description here",
        "prj_url": "https//noneOfYourBusiness.com"
    }

    @tag('prj', 'form', 'valid_data')
    def test_prj_valid_data(self):
        form = forms.PrjForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)
