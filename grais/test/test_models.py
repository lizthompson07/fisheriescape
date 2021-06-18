from django.test import tag

from shared_models import models as shared_models
from shared_models.test.common_tests import CommonTest
from . import FactoryFloor
from .. import models


class TestSpeciesModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()

    @tag('Species', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('Species', 'models', 'choices')
    def test_choices_field_that_has_choices(self):
        actual_choices = (
            (None, "-----"),
            ('ses', "sessile"),
            ('mob', "mobile"),
        )
        expected_choices = [field.choices for field in models.Species._meta.fields if field.name == "epibiont_type"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestSampleModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()

    @tag('Sample', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('Sample', 'models', 'choices')
    def test_choices_field_that_has_choices(self):
        actual_choices = (
            ('first', "first"),
            ('second', "second"),
            ('full', 'full'),
        )
        expected_choices = [field.choices for field in models.Sample._meta.fields if field.name == "sample_type"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestSurfaceModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SurfaceFactory()

    @tag('Surface', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('Surface', 'models', 'choices')
    def test_choices_field_that_has_choices(self):
        actual_choices = (
            ('pe', 'Petri dish'),
            ('pl', 'Plate'),
        )
        expected_choices = [field.choices for field in models.Surface._meta.fields if field.name == "surface_type"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestProbeMeasurementModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProbeMeasurementFactory()

    @tag('ProbeMeasurement', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('ProbeMeasurement', 'models', 'choices')
    def test_choices_field_that_has_choices(self):
        actual_choices = (
            ('AST', 'AST'),
            ('ADT', 'ADT'),
            ('UTC', 'UTC'),
        )
        expected_choices = [field.choices for field in models.ProbeMeasurement._meta.fields if field.name == "timezone"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestIncidentalReportModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.IncidentalReportFactory()

    @tag('IncidentalReport', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('IncidentalReport', 'models', 'choices')
    def test_choices_field_that_has_choices1(self):
        actual_choices = (
            (1, 'Gulf AIS Hotline'),
            (2, 'Gulf Invaders E-mail'),
            (3, 'Personal E-mail'),
        )
        expected_choices = [field.choices for field in models.IncidentalReport._meta.fields if field.name == "report_source"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('IncidentalReport', 'models', 'choices')
    def test_choices_field_that_has_choices2(self):
        actual_choices = (
            (1, 'English'),
            (2, 'French'),
        )
        expected_choices = [field.choices for field in models.IncidentalReport._meta.fields if field.name == "language_of_report"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('IncidentalReport', 'models', 'choices')
    def test_choices_field_that_has_choices3(self):
        actual_choices = (
            (1, 'Single observation'),
            (2, 'Ongoing presence'),
        )
        expected_choices = [field.choices for field in models.IncidentalReport._meta.fields if field.name == "observation_type"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('IncidentalReport', 'models', 'choices')
    def test_choices_field_that_has_choices4(self):
        actual_choices = (
            (1, "Public"),
            (2, "Academia"),
            (3, "Private sector"),
            (4, "Provincial government"),
            (5, "Federal government"),
        )
        expected_choices = [field.choices for field in models.IncidentalReport._meta.fields if field.name == "requestor_type"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestGCSampleModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.GCSampleFactory()

    @tag('GCSample', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('GCSample', 'models', 'choices')
    def test_choices_field_that_has_choices(self):
        actual_choices = (
            (1, 'Sand'),
            (2, 'Mud'),
            (3, 'Sand / Mud'),
        )
        expected_choices = [field.choices for field in models.GCSample._meta.fields if field.name == "sediment"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestGCProbeMeasurementModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.GCProbeMeasurementFactory()

    @tag('GCProbeMeasurement', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('GCProbeMeasurement', 'models', 'choices')
    def test_choices_field_that_has_choices(self):
        actual_choices = (
            ('l', "High"),
            ('m', "Mid"),
            ('h', "Low"),
        )
        expected_choices = [field.choices for field in models.GCProbeMeasurement._meta.fields if field.name == "tide_state"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('GCProbeMeasurement', 'models', 'choices')
    def test_choices_field_that_has_choices1(self):
        actual_choices = (
            ('in', "Incoming"),
            ('out', "Outgoing"),
        )
        expected_choices = [field.choices for field in models.GCProbeMeasurement._meta.fields if field.name == "tide_direction"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('GCProbeMeasurement', 'models', 'choices')
    def test_choices_field_that_has_choices2(self):
        actual_choices = (
            ('AST', 'AST'),
            ('ADT', 'ADT'),
            ('UTC', 'UTC'),
        )
        expected_choices = [field.choices for field in models.GCProbeMeasurement._meta.fields if field.name == "timezone"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestTrapModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TrapFactory()

    @tag('Trap', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('Trap', 'models', 'choices')
    def test_choices_field_that_has_choices(self):
        actual_choices = (
            (1, 'Fukui'),
            (2, 'Minnow'),
        )
        expected_choices = [field.choices for field in models.Trap._meta.fields if field.name == "trap_type"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestCatchModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.CatchFactory()

    @tag('Catch', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.MetadataFields)

    @tag('Catch', 'models', 'choices')
    def test_choices_field_that_has_choices(self):
        actual_choices = (
            (1, 'Male'),
            (2, 'Female'),
            (9, 'Unknown'),
        )
        expected_choices = [field.choices for field in models.Catch._meta.fields if field.name == "sex"][0]
        self.assertEqual(actual_choices, expected_choices)
