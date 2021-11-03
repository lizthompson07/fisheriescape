from django.test import tag
from django.utils.translation import gettext as _

from shared_models import models as shared_models
from shared_models.test.common_tests import CommonTest
from . import FactoryFloor
from .. import models


class TestRegionModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.RegionFactory()

    @tag('Region', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["abbreviation", "province"]
        self.assert_has_fields(models.Region, fields_to_check)

    @tag('Region', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Region, ["samples"])

    @tag('Region', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.UnilingualLookup)


class TestSiteModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SiteFactory()

    @tag('Site', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'abbreviation',
            'region',
            'latitude',
            'latitude_d',
            'latitude_mm',
            'longitude',
            'longitude_d',
            'longitude_mm',
        ]
        self.assert_has_fields(models.Site, fields_to_check)

    @tag('Site', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Site, [
            "transect_count",
            "coordinates",
            "get_coordinates_ddmm",
            "get_coordinates",
        ])

    @tag('Site', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.UnilingualLookup)

    @tag('Site', 'models', '12m')
    def test_12m_region(self):
        # a `site` that is attached to a given `region` should be accessible by the reverse name `sites`
        region = FactoryFloor.RegionFactory()
        my_instance = self.instance
        my_instance.region = region
        my_instance.save()
        self.assertIn(my_instance, region.sites.all())

    @tag('Site', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['region', ]
        self.assert_mandatory_fields(models.Site, fields_to_check)


class TestTransectModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TransectFactory()

    @tag('Transect', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'name',
            'site',
            'start_latitude_d',
            'start_latitude_mm',
            'start_longitude_d',
            'start_longitude_mm',
            'end_latitude_d',
            'end_latitude_mm',
            'end_longitude_d',
            'end_longitude_mm',
            'start_latitude',
            'start_longitude',
            'end_latitude',
            'end_longitude',
        ]
        self.assert_has_fields(models.Transect, fields_to_check)

    @tag('Transect', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Transect, [
            "get_starting_coordinates",
            "get_ending_coordinates",
            "transect_distance",
            "starting_coordinates_ddmm",
            "ending_coordinates_ddmm",
            "has_coordinates",
        ])

    @tag('Transect', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.UnilingualLookup)

    @tag('Transect', 'models', '12m')
    def test_12m_site(self):
        # a `transect` that is attached to a given `site` should be accessible by the reverse name `transects`
        site = FactoryFloor.SiteFactory()
        my_instance = self.instance
        my_instance.site = site
        my_instance.save()
        self.assertIn(my_instance, site.transects.all())

    @tag('Transect', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('name', 'site'),)
        actual_unique_together = models.Transect._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('Transect', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['site', ]
        self.assert_mandatory_fields(models.Transect, fields_to_check)


class TestDiverModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DiverFactory()

    @tag('Diver', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["first_name", 'last_name']
        self.assert_has_fields(models.Diver, fields_to_check)

    @tag('Diver', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Diver, ["dive_count"])

    @tag('Diver', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (("first_name", 'last_name'),)
        actual_unique_together = models.Diver._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)


class TestSampleModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()

    @tag('Sample', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            "site",
            "datetime",
            "weather_notes",
            "comment",
        ]
        self.assert_has_fields(models.Sample, fields_to_check)

    @tag('Sample', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Sample, ["site_region", 'dive_count'])

    @tag('Sample', 'models', '12m')
    def test_12m_site(self):
        # a `sample` that is attached to a given `site` should be accessible by the reverse name `samples`
        site = FactoryFloor.SiteFactory()
        my_instance = self.instance
        my_instance.site = site
        my_instance.save()
        self.assertIn(my_instance, site.samples.all())

    @tag('Sample', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['site', 'datetime']
        self.assert_mandatory_fields(models.Sample, fields_to_check)


class TestDiveModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DiveFactory()

    @tag('Dive', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'sample',
            'transect',
            'diver',
            'start_descent',
            'bottom_time',
            'max_depth_ft',
            'psi_in',
            'psi_out',
            'start_latitude_d',
            'start_latitude_mm',
            'start_longitude_d',
            'start_longitude_mm',
            'end_latitude_d',
            'end_latitude_mm',
            'end_longitude_d',
            'end_longitude_mm',
            'heading',
            'side',
            'width_m',
            'comment',
            'start_latitude',
            'start_longitude',
            'end_latitude',
            'end_longitude',
        ]
        self.assert_has_fields(models.Dive, fields_to_check)

    @tag('Dive', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Dive, [
            "starting_coordinates_ddmm",
            "ending_coordinates_ddmm",
            "observation_count",
            "get_starting_coordinates",
            "get_ending_coordinates",
            "dive_distance",
        ])

    @tag('Dive', 'models', '12m')
    def test_12m_sample(self):
        # a `dive` that is attached to a given `sample` should be accessible by the reverse name `dives`
        sample = FactoryFloor.SampleFactory()
        my_instance = self.instance
        my_instance.sample = sample
        my_instance.save()
        self.assertIn(my_instance, sample.dives.all())

    @tag('Dive', 'models', '12m')
    def test_12m_transect(self):
        # a `dive` that is attached to a given `transect` should be accessible by the reverse name `dives`
        transect = FactoryFloor.TransectFactory()
        my_instance = self.instance
        my_instance.transect = transect
        my_instance.save()
        self.assertIn(my_instance, transect.dives.all())

    @tag('Dive', 'models', '12m')
    def test_12m_diver(self):
        # a `dive` that is attached to a given `diver` should be accessible by the reverse name `dives`
        diver = FactoryFloor.DiverFactory()
        my_instance = self.instance
        my_instance.diver = diver
        my_instance.save()
        self.assertIn(my_instance, diver.dives.all())

    @tag('Dive', 'models', 'choices')
    def test_choices_heading(self):
        actual_choices = (
            ('n', _("North")),
            ('ne', _("Northeast")),
            ('e', _("East")),
            ('se', _("Southeast")),
            ('s', _("South")),
            ('sw', _("Southwest")),
            ('w', _("West")),
            ('nw', _("Northwest")),

        )
        expected_choices = [field.choices for field in models.Dive._meta.fields if field.name == "heading"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Dive', 'models', 'choices')
    def test_choices_side(self):
        actual_choices = (
            ('l', _("Left")),
            ('r', _("Right")),
        )
        expected_choices = [field.choices for field in models.Dive._meta.fields if field.name == "side"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Dive', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = [
            'sample',
            'transect',
            'diver',
            'width_m',
        ]
        self.assert_mandatory_fields(models.Dive, fields_to_check)


class TestSectionModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SectionFactory()

    @tag('Section', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'dive',
            'interval',
            'depth_ft',
            'percent_sand',
            'percent_mud',
            'percent_hard',
            'percent_algae',
            'percent_gravel',
            'percent_cobble',
            'percent_pebble',
            'comment',
        ]
        self.assert_has_fields(models.Section, fields_to_check)

    @tag('Section', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Section, ["substrate_profile"])

    @tag('Section', 'models', '12m')
    def test_12m_dive(self):
        # a `section` that is attached to a given `dive` should be accessible by the reverse name `sections`
        dive = FactoryFloor.DiveFactory()
        my_instance = self.instance
        my_instance.dive = dive
        my_instance.save()
        self.assertIn(my_instance, dive.sections.all())

    @tag('Section', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('dive', 'interval'),)
        actual_unique_together = models.Section._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('Section', 'models', 'choices')
    def test_choices_interval(self):
        actual_choices = (
            (1, "1 (0-5m)"),
            (2, "2 (5-10m)"),
            (3, "3 (10-15m)"),
            (4, "4 (15-20m)"),
            (5, "5 (20-25m)"),
            (6, "6 (25-30m)"),
            (7, "7 (30-35m)"),
            (8, "8 (35-40m)"),
            (9, "9 (40-45m)"),
            (10, "10 (45-50m)"),
            (11, "11 (50-55m)"),
            (12, "12 (55-60m)"),
            (13, "13 (60-65m)"),
            (14, "14 (65-70m)"),
            (15, "15 (70-75m)"),
            (16, "16 (75-80m)"),
            (17, "17 (80-85m)"),
            (18, "18 (85-90m)"),
            (19, "19 (90-95m)"),
            (20, "20 (95-100m)"),
        )
        expected_choices = [field.choices for field in models.Section._meta.fields if field.name == "interval"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Section', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['dive', 'interval']
        self.assert_mandatory_fields(models.Section, fields_to_check)


class TestObservationModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ObservationFactory()

    @tag('Observation', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'section',
            'sex',
            'egg_status',
            'carapace_length_mm',
            'certainty_rating',
            'comment',
        ]
        self.assert_has_fields(models.Observation, fields_to_check)

    @tag('Observation', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Observation, [
            'sex_special_display',
            'egg_status_special_display',
            'certainty_rating_special_display',
        ])

    @tag('Observation', 'models', '12m')
    def test_12m_section(self):
        # a `observation` that is attached to a given `section` should be accessible by the reverse name `observations`
        section = FactoryFloor.SectionFactory()
        my_instance = self.instance
        my_instance.section = section
        my_instance.save()
        self.assertIn(my_instance, section.observations.all())

    @tag('Observation', 'models', 'choices')
    def test_choices_sex(self):
        actual_choices = (
            ('u', _("0 - unknown")),
            ('m', _("1 - male")),
            ('f', _("2 - female")),
        )
        expected_choices = [field.choices for field in models.Observation._meta.fields if field.name == "sex"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Observation', 'models', 'choices')
    def test_choices_egg_status(self):
        actual_choices = (
            ("0", _("0 - no eggs")),
            ("b", _("b - berried")),
            ("b1", _("b1 - berried with new eggs")),
            ("b2", _("b2 - berried with black eggs")),
            ("b3", _("b3 - berried with developed eggs")),
        )
        expected_choices = [field.choices for field in models.Observation._meta.fields if field.name == "egg_status"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Observation', 'models', 'choices')
    def test_choices_certainty_rating(self):
        actual_choices = (
            (1, _("1 - certain")),
            (0, _("0 - uncertain")),
        )
        expected_choices = [field.choices for field in models.Observation._meta.fields if field.name == "certainty_rating"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Observation', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['section', 'sex', 'certainty_rating']
        self.assert_mandatory_fields(models.Observation, fields_to_check)
