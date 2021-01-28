from datetime import timedelta

from django.db.models import Q
from django.test import tag
from django.utils import timezone

from shared_models.test.common_tests import CommonTest
from .FactoryFloor import SampleFactory, DiveFactory
from .. import forms
from ..test import FactoryFloor as FactoryFloor

class TestDiveForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.dive = DiveFactory()

        self.Form = forms.DiveForm

    @tag("Dive", 'forms')
    def test_valid_data(self):

        # modifying an old dive
        data = FactoryFloor.DiveFactory.get_valid_data(self.dive.sample)
        self.assert_form_valid(self.Form, data=data, instance=self.dive)

        # the transect must belong to the same site as the sample!
        data = FactoryFloor.DiveFactory.get_invalid_data()
        self.assert_form_invalid(self.Form, data=data, instance=self.dive)

        # the start descent time must be in sync with sample datetime!
        data = FactoryFloor.DiveFactory.get_valid_data(self.dive.sample)
        new_dt = self.dive.sample.datetime + timedelta(seconds=10)
        data['start_descent'] = new_dt
        self.assert_form_valid(self.Form, data=data, instance=self.dive)

        new_dt = self.dive.sample.datetime + timedelta(days=1)
        data['start_descent'] = new_dt
        self.assert_form_invalid(self.Form, data=data, instance=self.dive)

        # new dive
        data = FactoryFloor.DiveFactory.get_valid_data(self.dive.sample)
        initial = dict(sample=self.dive.sample.id)
        self.assert_form_valid(self.Form, data=data, initial=initial)

        # the transect must belong to the same site as the sample!
        data = FactoryFloor.DiveFactory.get_invalid_data()
        self.assert_form_invalid(self.Form, data=data, initial=initial)

        # the start descent time must be in sync with sample datetime!
        data = FactoryFloor.DiveFactory.get_valid_data(self.dive.sample)
        new_dt = self.dive.sample.datetime + timedelta(seconds=10)
        data['start_descent'] = new_dt
        self.assert_form_valid(self.Form, data=data, initial=initial)

        new_dt = self.dive.sample.datetime + timedelta(days=1)
        data['start_descent'] = new_dt
        self.assert_form_invalid(self.Form, data=data, initial=initial)

