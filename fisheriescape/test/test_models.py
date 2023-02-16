from django.urls import reverse_lazy
from django.test import tag

import shared_models
from fisheriescape import models
from fisheriescape.test import FactoryFloor
from fisheriescape.test.common_tests import CommonFisheriescapeTest as CommonTest
from faker import Faker

faker = Faker()

# Example how to run with keyword tags
# python manage.py test fisheriescape.test --tag models


# TODO self.instance doesn't call anything
class TestFisheryAreaModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FisheryAreaFactory()

    @tag('FisheryArea', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            "layer_id",
            "name",
            "nafo_area",
            "region",
            "polygon",
        ]
        self.assert_has_fields(models.FisheryArea, fields_to_check)

    @tag('FisheryArea', 'models', 'm2m')
    def test_m2m_NAFOArea(self):
        # a `my_model` that is attached to a given `NAFOArea` should be accessible by the m2m field name `NAFOAreas`
        NAFOArea = FactoryFloor.NAFOAreaFactory()
        self.instance.nafo_area.add(NAFOArea)
        self.assertEqual(self.instance.nafo_area.count(), 1)
        self.assertIn(NAFOArea, self.instance.nafo_area.all())

    @tag('FisheryArea', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('name', 'layer_id'),)
        actual_unique_together = models.FisheryArea._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('FisheryArea', 'models', 'choices')
    def test_choices_region(self):
        actual_choices = (
            ("Gulf", "Gulf"),
            ("Mar", "Maritimes"),
            ("NL", "Newfoundland"),
            ("QC", "Quebec"),
        )
        expected_choices = [field.choices for field in models.FisheryArea._meta.fields if field.name == "region"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('FisheryArea', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['polygon', ]
        self.assert_mandatory_fields(models.FisheryArea, fields_to_check)


class TestNAFOAreaModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.NAFOAreaFactory()

    @tag('NAFOArea', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            "layer_id",
            "name",
            "polygon",
        ]
        self.assert_has_fields(models.NAFOArea, fields_to_check)

    @tag('NAFOArea', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('name', 'layer_id'),)
        actual_unique_together = models.NAFOArea._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('NAFOArea', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['polygon', ]
        self.assert_mandatory_fields(models.NAFOArea, fields_to_check)


class TestMarineMammalModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.MarineMammalFactory()

    @tag('MarineMammal', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            "english_name",
            "english_name_short",
            "french_name",
            "french_name_short",
            "latin_name",
            "population",
            "sara_status",
            "cosewic_status",
            "website",
        ]
        self.assert_has_fields(models.MarineMammal, fields_to_check)

    @tag('MarineMammal', 'models', 'choices')
    def test_choices_sara_status(self):
        actual_choices = (
            ("No Status", "No Status"),
            ("Not at Risk", "Not at Risk"),
            ("Special Concern", "Special Concern"),
            ("Threatened", "Threatened"),
            ("Endangered", "Endangered"),
            ("Extirpated", "Extirpated"),
            ("Extinct", "Extinct"),
        )
        expected_choices = [field.choices for field in models.MarineMammal._meta.fields if field.name == "sara_status"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('MarineMammal', 'models', 'choices')
    def test_choices_cosewic_status(self):
        actual_choices = (
            ("No Status", "No Status"),
            ("Not at Risk", "Not at Risk"),
            ("Special Concern", "Special Concern"),
            ("Threatened", "Threatened"),
            ("Endangered", "Endangered"),
            ("Extirpated", "Extirpated"),
            ("Extinct", "Extinct"),
        )
        expected_choices = [field.choices for field in models.MarineMammal._meta.fields if field.name == "sara_status"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestFisheryModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FisheryFactory()

    @tag('Fishery', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            "species",
            "participants",
            "participant_detail",
            "start_date",
            "end_date",
            "gear_type",
            "gear_amount",
            "gear_config",
            "gear_soak",
            "gear_primary_colour",
            "gear_secondary_colour",
            "gear_tertiary_colour",
            "gear_comment",
            "monitoring_aso",
            "monitoring_dockside",
            "monitoring_logbook",
            "monitoring_vms",
            "monitoring_comment",
            "mitigation_comment",
        ]
        self.assert_has_fields(models.Fishery, fields_to_check)

    @tag('Fishery', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Fishery, ["nafo_fishery_areas"])

    @tag('Fishery', 'models', 'm2m')
    def test_m2m_marine_mammal(self):
        # a `my_model` that is attached to a given `marine_mammals` should be accessible by the m2m field name `marine_mammals`
        marine_mammals = FactoryFloor.MarineMammalFactory()
        self.instance.marine_mammals.add(marine_mammals)
        self.assertEqual(self.instance.marine_mammals.count(), 1)
        self.assertIn(marine_mammals, self.instance.marine_mammals.all())

    @tag('Fishery', 'models', 'm2m')
    def test_m2m_fishery_areas(self):
        # a `my_model` that is attached to a given `fishery_areas` should be accessible by the m2m field name `fishery_areas`
        fishery_areas = FactoryFloor.FisheryAreaFactory()
        self.instance.fishery_areas.add(fishery_areas)
        self.assertEqual(self.instance.fishery_areas.count(), 1)
        self.assertIn(fishery_areas, self.instance.fishery_areas.all())

    @tag('Fishery', 'models', 'm2m')
    def test_m2m_mitigation(self):
        # a `my_model` that is attached to a given `mitigation` should be accessible by the m2m field name `mitigation`
        mitigation = FactoryFloor.MitigationFactory()
        self.instance.mitigation.add(mitigation)
        self.assertEqual(self.instance.mitigation.count(), 1)
        self.assertIn(mitigation, self.instance.mitigation.all())

    @tag('Fishery', 'models', 'choices')
    def test_choices_fishery_status(self):
        actual_choices = (
            ("Active", "Active"),
            ("Experimental", "Experimental"),
            ("Inactive", "Inactive"),
            ("Unknown", "Unknown"),
        )
        expected_choices = [field.choices for field in models.Fishery._meta.fields if field.name == "fishery_status"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Fishery', 'models', 'choices')
    def test_choices_license_type(self):
        actual_choices = (
            ("Multi", "Multi Species"),
            ("Single", "Single Species"),
        )
        expected_choices = [field.choices for field in models.Fishery._meta.fields if field.name == "license_type"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Fishery', 'models', 'choices')
    def test_choices_management_system(self):
        actual_choices = (
            ("Effort Control", "Effort Control"),
            ("Quota - Competitive", "Quota - Competitive"),
            ("Quota - Individual", "Quota - Individual"),
        )
        expected_choices = [field.choices for field in models.Fishery._meta.fields if field.name == "management_system"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Fishery', 'models', 'choices')
    def test_choices_gear_type(self):
        actual_choices = (
            ("Gillnets", "Gillnets"),
            ("Longlines", "Longlines"),
            ("Pots / Traps", "Pots / Traps"),
            ("Set Gillnet", "Set Gillnet"),
        )
        expected_choices = [field.choices for field in models.Fishery._meta.fields if field.name == "gear_type"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Fishery', 'models', 'choices')
    def test_choices_gear_primary_colour(self):
        actual_choices = (
            ("", "---------"),
            ("Blue", "Blue"),
            ("Black", "Black"),
            ("Red", "Red"),
            ("Yellow", "Yellow"),
            ("White", "White"),
            ("Purple", "Purple"),
            ("Orange", "Orange"),
            ("Green", "Green"),
            ("Grey", "Grey"),
            ("Brown", "Brown"),
            ("Pink", "Pink"),
            ("Red/White Pattern", "Red/White Pattern"),
        )
        expected_choices = [field.choices for field in models.Fishery._meta.fields if field.name == "gear_primary_colour"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Fishery', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = [
            'species',
        ]
        self.assert_mandatory_fields(models.Fishery, fields_to_check)
