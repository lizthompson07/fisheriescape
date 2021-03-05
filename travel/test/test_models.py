from django.test import tag
from django.utils.translation import gettext as _
from faker import Faker

from shared_models import models as shared_models
from shared_models.test.SharedModelsFactoryFloor import SectionFactory, RegionFactory, BranchFactory, DivisionFactory
from travel.test.common_tests import CommonTravelTest as CommonTest
from . import FactoryFloor
from .. import models

faker = Faker()


class TestHelpTextModel(CommonTest):
    def setUp(self):
        super().setUp()

    @tag('HelpText', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'field_name',
            'eng_text',
            'fra_text',
        ]
        self.assert_has_fields(models.HelpText, fields_to_check)

    @tag('HelpText', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['field_name', ]
        self.assert_mandatory_fields(models.HelpText, fields_to_check)


class TestDefaultReviewerModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DefaultReviewerFactory()

    @tag('DefaultReviewer', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'user',
            'expenditure_initiation_region',
            'special_role',
            'order',
        ]
        self.assert_has_fields(models.DefaultReviewer, fields_to_check)

    @tag('DefaultReviewer', 'models', '12m')
    def test_12m_expenditure_initiation_region(self):
        # a `default_reviewer` that is attached to a given `expenditure_initiation_region` should be accessible by the reverse name `default_reviewers`
        expenditure_initiation_region = RegionFactory()
        my_instance = self.instance
        my_instance.expenditure_initiation_region = expenditure_initiation_region
        my_instance.save()
        self.assertIn(my_instance, expenditure_initiation_region.travel_default_reviewers.all())

    @tag('DefaultReviewer', 'models', 'm2m')
    def test_m2m_sections(self):
        # a `default_reviewer` that is attached to a given `sections` should be accessible by the m2m field name `sections`
        section = SectionFactory()
        self.instance.sections.add(section)
        self.assertEqual(self.instance.sections.count(), 1)
        self.assertIn(section, self.instance.sections.all())

    @tag('DefaultReviewer', 'models', 'm2m')
    def test_m2m_divisions(self):
        # a `default_reviewer` that is attached to a given `divisions` should be accessible by the m2m field name `divisions`
        division = DivisionFactory()
        self.instance.divisions.add(division)
        self.assertEqual(self.instance.divisions.count(), 1)
        self.assertIn(division, self.instance.divisions.all())

    @tag('DefaultReviewer', 'models', 'm2m')
    def test_m2m_branches(self):
        # a `default_reviewer` that is attached to a given `branch` should be accessible by the m2m field name `branches`
        branch = BranchFactory()
        self.instance.branches.add(branch)
        self.assertEqual(self.instance.branches.count(), 1)
        self.assertIn(branch, self.instance.branches.all())

    @tag('DefaultReviewer', 'models', 'choices')
    def test_special_role(self):
        actual_choices = (
            (3, _("NCR Travel Coordinators")),
            (4, _("ADM Recommender")),
            (5, _("ADM")),
        )
        expected_choices = [field.choices for field in models.DefaultReviewer._meta.fields if field.name == "special_role"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('DefaultReviewer', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['user', ]
        self.assert_mandatory_fields(models.DefaultReviewer, fields_to_check)


class TestNJCRatesModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.NJCRates.objects.all()[faker.random_int(0, models.NJCRates.objects.count() - 1)]

    @tag('NJCRates', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["amount", "last_modified", ]
        self.assert_has_fields(models.NJCRates, fields_to_check)

    @tag('NJCRates', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)

    @tag('NJCRates', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['amount', ]
        self.assert_mandatory_fields(models.NJCRates, fields_to_check)


class TestProcessStepModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProcessStepFactory()

    @tag('ProcessStep', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'stage',
            'order',
            'is_visible',
        ]
        self.assert_has_fields(models.ProcessStep, fields_to_check)

    @tag('ProcessStep', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.Lookup)

    @tag('ProcessStep', 'models', 'choices')
    def test_choices_stage(self):
        actual_choices = (
            (0, _("Information Section")),
            (1, _("Travel Request Process Outline")),
            (2, _("Review Process Outline")),
        )
        expected_choices = [field.choices for field in models.ProcessStep._meta.fields if field.name == "stage"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestFAQModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FAQFactory()

    @tag('FAQ', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'question_en',
            'question_fr',
            'answer_en',
            'answer_fr',
            'order',
        ]
        self.assert_has_fields(models.FAQ, fields_to_check)

    @tag('FAQ', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.FAQ, ["tquestion", "tanswer"])


class TestReferenceMaterialModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReferenceMaterialFactory()

    @tag('ReferenceMaterial', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'order',
            'url_en',
            'url_fr',
            'file_en',
            'file_fr',
            'created_at',
            'updated_at',
        ]
        self.assert_has_fields(models.ReferenceMaterial, fields_to_check)

    @tag('ReferenceMaterial', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.ReferenceMaterial, [
            "tfile",
            "turl",
        ])

    @tag('ReferenceMaterial', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)


class TestCostCategoryModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.CostCategory.objects.all()[faker.random_int(0, models.CostCategory.objects.count() - 1)]

    @tag('CostCategory', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["order", ]
        self.assert_has_fields(models.CostCategory, fields_to_check)

    @tag('CostCategory', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)


class TestCostModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.Cost.objects.all()[faker.random_int(0, models.Cost.objects.count() - 1)]

    @tag('Cost', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["cost_category", ]
        self.assert_has_fields(models.Cost, fields_to_check)

    @tag('Cost', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)

    @tag('Cost', 'models', '12m')
    def test_12m_cost_category(self):
        # a `cost` that is attached to a given `cost_category` should be accessible by the reverse name `costs`
        cost_category = models.CostCategory.objects.all()[faker.random_int(0, models.CostCategory.objects.count() - 1)]
        my_instance = self.instance
        my_instance.cost_category = cost_category
        my_instance.save()
        self.assertIn(my_instance, cost_category.cost_set.all())


class TestRoleModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.RoleFactory()

    @tag('Role', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)


class TestTripCategoryModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.TripCategory.objects.all()[faker.random_int(0, models.TripCategory.objects.count() - 1)]

    @tag('TripCategory', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["days_when_eligible_for_review", ]
        self.assert_has_fields(models.TripCategory, fields_to_check)

    @tag('TripCategory', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)


class TestTripSubcategoryModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.TripSubcategory.objects.all()[faker.random_int(0, models.TripSubcategory.objects.count() - 1)]

    @tag('TripSubcategory', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["trip_category", ]
        self.assert_has_fields(models.TripSubcategory, fields_to_check)

    @tag('TripSubcategory', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.TripSubcategory, ["tname"])

    @tag('TripSubcategory', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.Lookup)

    @tag('TripSubcategory', 'models', '12m')
    def test_12m_trip_category(self):
        # a `trip_subcategory` that is attached to a given `trip_category` should be accessible by the reverse name `subcategories`
        trip_category = models.TripCategory.objects.all()[faker.random_int(0, models.TripCategory.objects.count() - 1)]
        my_instance = self.instance
        my_instance.trip_category = trip_category
        my_instance.save()
        self.assertIn(my_instance, trip_category.subcategories.all())


class TestTripModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()

    @tag('Trip', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'abstract_deadline',
            'adm_review_deadline',
            'admin_notes',
            'cost_warning_sent',
            'created_at',
            'created_by',
            'date_eligible_for_adm_review',
            'end_date',
            'fiscal_year',
            'has_event_template',
            'is_adm_approval_required',
            'is_verified',
            'is_virtual',
            'lead',
            'location',
            'meeting_url',
            'name',
            'nom',
            'notes',
            'number',
            'registration_deadline',
            'review_start_date',
            'start_date',
            'status',
            'trip_subcategory',
            'updated_at',
            'updated_by',
            'verified_by',
        ]
        self.assert_has_fields(models.Trip, fields_to_check)

    @tag('Trip', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Trip, ['metadata',
                                            'closest_date',
                                            'days_until_eligible_for_adm_review',
                                            'days_until_adm_review_deadline',
                                            'admin_notes_html',
                                            'html_block',
                                            'number_of_days',
                                            'dates',
                                            'travellers',
                                            'total_cost',
                                            'total_non_dfo_cost',
                                            'total_dfo_cost',
                                            'non_res_total_cost',
                                            'total_non_dfo_funding_sources',
                                            'tname',
                                            'current_reviewer',
                                            'trip_review_ready',
                                            ])

    @tag('Trip', 'models', '12m')
    def test_12m_trip_subcategory(self):
        # a `trip` that is attached to a given `trip_subcategory` should be accessible by the reverse name `trips`
        # trip_subcategory = FactoryFloor.TripSubcategoryFactory()
        trip_subcategory = models.TripSubcategory.objects.all()[faker.random_int(0, models.TripSubcategory.objects.count() - 1)]
        my_instance = self.instance
        my_instance.trip_subcategory = trip_subcategory
        my_instance.save()
        self.assertIn(my_instance, trip_subcategory.trips.all())

    @tag('Trip', 'models', '12m')
    def test_12m_trip_subcategory(self):
        # a `trip` that is attached to a given `trip_subcategory` should be accessible by the reverse name `trips`
        # trip_subcategory = FactoryFloor.TripSubcategoryFactory()
        trip_subcategory = models.TripSubcategory.objects.all()[faker.random_int(0, models.TripSubcategory.objects.count() - 1)]
        my_instance = self.instance
        my_instance.trip_subcategory = trip_subcategory
        my_instance.save()
        self.assertIn(my_instance, trip_subcategory.trips.all())

    @tag('Trip', 'models', '12m')
    def test_12m_lead(self):
        # a `trip` that is attached to a given `region` should be accessible by the reverse name `trips`
        region = FactoryFloor.RegionFactory()
        my_instance = self.instance
        my_instance.lead = region
        my_instance.save()
        self.assertIn(my_instance, region.meeting_leads.all())

    @tag('Trip', 'models', 'choices')
    def test_choices_status(self):
        actual_choices = (
            (30, _("Unverified")),
            (31, _("Under review")),
            (32, _("Reviewed")),
            (41, _("Verified")),
            (43, _("Cancelled")),
        )
        expected_choices = [field.choices for field in models.Trip._meta.fields if field.name == "status"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Trip', 'models', 'unique_fields')
    def test_unique_fields(self):
        fields_to_check = ['name', ]
        self.assert_unique_fields(models.Trip, fields_to_check)

    @tag('Trip', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = [
            'name',
            'is_virtual',
            'start_date',
            'end_date',
        ]
        self.assert_mandatory_fields(models.Trip, fields_to_check)
