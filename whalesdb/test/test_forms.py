from django.test import TestCase, tag

from whalesdb import forms


class TestMorForm(TestCase):
    valid_data = {
        "stn_name": "STN_001",
        "stn_code": "STN",
        "stn_revision": "1",
        "stn_planned_lat": "25",
        "stn_planned_lon": "50",
        "stn_planned_depth": "10",
        "stn_notes": "Some Notes"
    }

    @tag('stn_form', 'valid_data')
    def test_stn_valid_data(self):
        form = forms.StnForm(data=self.valid_data)
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

    @tag('stn_form', 'valid_data')
    def test_stn_valid_data(self):
        form = forms.StnForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)


class TestPrjForm(TestCase):
    valid_data = {
            "stn_name": "STN_001",
            "stn_code": "STN",
            "stn_revision": "1",
            "stn_planned_lat": "25",
            "stn_planned_lon": "50",
            "stn_planned_depth": "10",
            "stn_notes": "Some Notes"
        }

    @tag('stn_form', 'valid_data')
    def test_stn_valid_data(self):
        form = forms.StnForm(data=self.valid_data)
        form.is_valid()
        self.assertFalse(form.errors)