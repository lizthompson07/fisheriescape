import datetime
from django.test import tag
from .. import forms
from masterlist import models as ml_models
from ihub.test import FactoryFloor
from ihub.test.common_tests import CommonIHubTest as CommonTest


class TestEntryCreateForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.EntryCreateForm

    @tag("trip_request", 'form')
    def test_valid_data(self):
        org = FactoryFloor.OrganizationFactory()
        grouping = ml_models.Grouping.objects.filter(is_indigenous=True).first()
        org.grouping.add(grouping)

        data = FactoryFloor.EntryFactory.get_valid_data()
        print(data)
        data["organizations"] = [org.id]
        data["sectors"] = [data["sectors"]]
        data["regions"] = [data["regions"]]

        self.assert_form_valid(self.Form, data=data)

        del data["regions"]
        del data["sectors"]
        del data["organizations"]
        self.assert_form_invalid(self.Form, data=data)
