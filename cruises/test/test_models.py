from django.test import tag
from faker import Faker

from shared_models.models import Cruise, Institute, Vessel
from shared_models.test.SharedModelsFactoryFloor import CruiseFactory
from shared_models import models as shared_models
from cruises.test.common_tests import CommonCruisesTest as CommonTest

faker = Faker()


class TestInstituteModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = shared_models.Institute.objects.all()[faker.random_int(0, shared_models.Institute.objects.count() - 1)]

    @tag('Institute', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'abbrev',
            'address',
            'region',
        ]
        self.assert_has_fields(shared_models.Institute, fields_to_check)

    @tag('Institute', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)


class TestCruiseModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = CruiseFactory()

    @tag('Cruise', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'institute',
            'mission_number',
            'mission_name',
            'description',
            'purpose',
            'chief_scientist',
            'samplers',
            'start_date',
            'end_date',
            'probe',
            'area_of_operation',
            'number_of_profiles',
            'meds_id',
            'notes',
            'season',
            'vessel',
            'west_bound_longitude',
            'east_bound_longitude',
            'north_bound_latitude',
            'south_bound_latitude',
            'funding_agency_name',
            'funding_project_title',
            'funding_project_id',
            'research_projects_programs',
            'references',
        ]
        self.assert_has_fields(Cruise, fields_to_check)

    @tag('Cruise', 'models', 'props')
    def test_props(self):
        self.assert_has_props(Cruise, ["time_period"])

    @tag('Cruise', 'models', '12m')
    def test_12m_institute(self):
        # a `cruise` that is attached to a given `institute` should be accessible by the reverse name `cruises`
        institute = Institute.objects.all()[faker.random_int(0, Institute.objects.count() - 1)]
        my_instance = self.instance
        my_instance.institute = institute
        my_instance.save()
        self.assertIn(my_instance, institute.cruises.all())

    @tag('Cruise', 'models', 'unique_fields')
    def test_unique_fields(self):
        fields_to_check = ['mission_number', ]
        self.assert_unique_fields(Cruise, fields_to_check)

    @tag('Cruise', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = [
            'mission_number',
            'mission_name',
            'chief_scientist',
        ]
        self.assert_mandatory_fields(Cruise, fields_to_check)


class TestVesselModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = Vessel.objects.all()[faker.random_int(0, Vessel.objects.count() - 1)]

    @tag('Vessel', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'name',
            'call_sign',
            'ices_shipc_ship_codes',
            'country_of_origin',
            'platform_type',
            'platform_owner',
            'imo_number',
        ]
        self.assert_has_fields(Vessel, fields_to_check)

    @tag('Vessel', 'models', 'unique_fields')
    def test_unique_fields(self):
        fields_to_check = ['name', 'call_sign']
        self.assert_unique_fields(Vessel, fields_to_check)

    @tag('Vessel', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['name', ]
        self.assert_mandatory_fields(Vessel, fields_to_check)
