from datetime import timedelta

from django.db.models import Q
from django.test import tag
from django.utils import timezone

from .. import forms
from ..models import FundingSource
from ..test import FactoryFloor as FactoryFloor
from ..test.common_tests import CommonProjectTest as CommonTest


class TestProjectYearForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.ProjectYearForm

    @tag("ProjectYear", 'forms')
    def test_valid_data(self):
        # get valid data
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        self.assert_form_valid(self.Form, data=data, initial=dict(project=FactoryFloor.ProjectFactory()))

        # end data cannot be after start date
        end_date = data["start_date"] - timedelta(days=3)
        data["end_date"] = end_date
        self.assert_form_invalid(self.Form, data=data, initial=dict(project=FactoryFloor.ProjectFactory()))

        # start and end dates must be within the same fiscal year
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        self.assert_form_valid(self.Form, data=data, initial=dict(project=FactoryFloor.ProjectFactory()))
        data["end_date"] += timedelta(days=30)
        self.assert_form_invalid(self.Form, data=data, initial=dict(project=FactoryFloor.ProjectFactory()))

        # if there is another project year in the same fiscal year,
        project = FactoryFloor.ProjectFactory()
        project_year1 = FactoryFloor.ProjectYearFactory(project=project, start_date=timezone.datetime(2018, 4, 1, tzinfo=timezone.get_current_timezone()))

        # try creating a new year with the  fiscal year same as year 1
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        data['start_date'] = project_year1.start_date
        data['end_date'] = None
        self.assert_form_invalid(self.Form, data=data, initial=dict(project=project))

        # now take an existing year and try submitting the form without changing the FY. it should be acceptable
        project_year2 = FactoryFloor.ProjectYearFactory(project=project, start_date=timezone.datetime(2019, 4, 1, tzinfo=timezone.get_current_timezone()))
        data = FactoryFloor.ProjectYearFactory.get_valid_data()
        data['start_date'] = project_year2.start_date
        data['end_date'] = project_year2.end_date
        data['project'] = project.id
        self.assert_form_valid(self.Form, data=data, instance=project_year2)
        # but if we are cloning the project year,  the logic should be reversed
        self.assert_form_invalid(self.Form, data=data, instance=project_year2, initial=dict(cloning=True))

        # if we try to change this to a FY where there is already a year, this should be invalid
        data['start_date'] = project_year1.start_date
        data['end_date'] = None
        self.assert_form_invalid(self.Form, data=data, instance=project_year2)


class TestProjectForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.ProjectForm


    @tag("ProjectYear", 'forms')
    def test_fields(self):
        instance = FactoryFloor.ProjectFactory()
        # if we are cloning, there should not be a "tags" field
        self.assert_field_not_in_form(self.Form, "tags", instance=instance, initial=dict(cloning=True))
        # if ACRDP we should have the following fields
        acrdp_funding_source = FactoryFloor.FundingSourceFactory(name="ACRDP")
        instance.default_funding_source = acrdp_funding_source
        instance.save()
        fields = [
            'organization',
            'species_involved',
            'team_description',
            'rationale',
            'experimental_protocol',
        ]
        for f in fields:
            self.assert_field_in_form(self.Form, f, instance=instance)
        # but if is not acrdp, then the fields should not be there
        funding_source = FactoryFloor.FundingSourceFactory()
        instance.default_funding_source = funding_source
        instance.save()
        for f in fields:
            self.assert_field_not_in_form(self.Form, f, instance=instance)

