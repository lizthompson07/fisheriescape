import os
from datetime import timedelta

from django.test import TestCase, tag
from django.conf import settings

from .. import reports, forms

from ..test import FactoryFloor as FactoryFloor
from ..test.common_tests import CommonProjectTest as CommonTest

from shared_models import models as shared_models
from shared_models.test.SharedModelsFactoryFloor import RegionFactory, BranchFactory, DivisionFactory, SectionFactory


class TestProjectYearForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.ProjectYearForm

    @tag("ProjectYear", 'forms')
    def test_valid_data(self):
        project =  FactoryFloor.ProjectFactory()
        project_year1 =  FactoryFloor.ProjectYearFactory(project=project)

        # get valid data
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        self.assert_form_valid(self.Form, data=data, initial=dict(project=project))

        # end data cannot be after start date
        end_date = data["start_date"] - timedelta(days=3)
        data["end_date"] = end_date
        self.assert_form_invalid(self.Form, data=data, instance=project_year1)

        # start and end dates must be within the same fiscal year
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        self.assert_form_valid(self.Form, data=data, initial=dict(project=project))
        data["end_date"] +=  timedelta(days=30)
        self.assert_form_invalid(self.Form, data=data, initial=dict(project=project))

        # if there is another project year in the same fiscal year,
        project_year2 =  FactoryFloor.ProjectYearFactory(project=project)
        project_year2.save()
        print(project_year2.fiscal_year)

        # try changing the fiscal year to the same as year 1
        # data = FactoryFloor.ProjectYearFactory.get_valid_data()
        # data['start_date'] = project_year1.start_date
        # data['end_date'] = None
        # self.assert_form_invalid(self.Form, data=data, instance=project_year2)
        # # but if we are cloning this logic should be reversed
        # self.assert_form_valid(self.Form, data=data, instance=project_year2, initial=dict(cloning=True))








    @tag("ProjectYear", 'forms')
    def test_fields(self):
        self.assert_field_not_in_form(self.Form, "reset_reviewers")

        instance = FactoryFloor.ProjectYearFactory()
        fields = []
        for f in fields:
            self.assert_field_in_form(self.Form, fields, instance=instance)

