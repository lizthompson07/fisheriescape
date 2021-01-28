from django.test import tag
from django.utils.translation import gettext as _
from faker import Factory

from shared_models import models as shared_models
from shared_models.test.SharedModelsFactoryFloor import CitationFactory, ProjectFactory
from . import FactoryFloor
from .. import models
from ..test.common_tests import CommonProjectTest as CommonTest

faker = Factory.create()


class TestFunctionalGroupModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FunctionalGroupFactory()

    @tag('FunctionalGroup', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)

    @tag('FunctionalGroup', 'models', '12m')
    def test_12m_theme(self):
        # a `functional_group` that is attached to a given `theme` should be accessible by the reverse name `functional_groups`
        theme = FactoryFloor.ThemeFactory()
        my_instance = self.instance
        my_instance.theme = theme
        my_instance.save()
        self.assertIn(my_instance, theme.functional_groups.all())

    @tag('FunctionalGroup', 'models', 'm2m')
    def test_m2m_sections(self):
        # a `functional_group` that is attached to a given `sections` should be accessible by the m2m field name `sections`
        sections = FactoryFloor.SectionFactory()
        self.instance.sections.add(sections)
        self.assertEqual(self.instance.sections.count(), 1)
        self.assertIn(sections, self.instance.sections.all())


class TestFundingSourceModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FundingSourceFactory()

    @tag('FundingSource', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["is_competitive", ]
        self.assert_has_fields(models.FundingSource, fields_to_check)

    @tag('FundingSource', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.FundingSource, ["display2", "display3"])

    @tag('FundingSource', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)

    @tag('FundingSource', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('funding_source_type', 'name'),)
        actual_unique_together = models.FundingSource._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('FundingSource', 'models', 'choices')
    def test_choices_funding_source_type(self):
        actual_choices = (
            (1, _("A-base")),
            (2, _("B-base")),
            (3, _("C-base")),
        )
        expected_choices = [field.choices for field in models.FundingSource._meta.fields if field.name == "funding_source_type"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('FundingSource', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['funding_source_type', ]
        self.assert_mandatory_fields(models.FundingSource, fields_to_check)


# class TestProjectModel(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.ProjectFactory()
#
#     @tag('Project', 'models', 'fields')
#     def test_fields(self):
#         fields_to_check = [
#             'section',
#             'title',
#             'activity_type',
#             'functional_group',
#             'default_funding_source',
#             'overview',
#             'is_hidden',
#             'organization',
#             'species_involved',
#             'team_description',
#             'rationale',
#             'experimental_protocol',
#             'client_information',
#             'second_priority',
#             'objectives',
#             'innovation',
#             'other_funding',
#             'start_date',
#             'end_date',
#             'staff_search_field',
#             'created_at',
#             'updated_at',
#             'modified_by',
#         ]
#         self.assert_has_fields(models.Project, fields_to_check)
#
#     @tag('Project', 'models', 'props')
#     def test_props(self):
#         self.assert_has_props(models.Project, [
#             "metadata",
#             "dates",
#             "has_unsubmitted_years",
#             "region",
#             "division",
#             "overview_html",
#             "objectives_html",
#             "innovation_html",
#             "other_funding_html",
#             "team_description_html",
#             "rationale_html",
#             "experimental_protocol_html",
#             "client_information_html",
#             "get_funding_sources",
#             "is_acrdp",
#             "is_csrf",
#             "fiscal_years",
#         ])
#
#     @tag('Project', 'models', '12m')
#     def test_12m_section(self):
#         # a `project` that is attached to a given `section` should be accessible by the reverse name `projects2`
#         section = FactoryFloor.SectionFactory()
#         my_instance = self.instance
#         my_instance.section = section
#         my_instance.save()
#         self.assertIn(my_instance, section.projects2.all())
#
#     @tag('Project', 'models', '12m')
#     def test_12m_functional_group(self):
#         # a `project` that is attached to a given `functional_group` should be accessible by the reverse name `projects2`
#         functional_group = FactoryFloor.FunctionalGroupFactory()
#         my_instance = self.instance
#         my_instance.functional_group = functional_group
#         my_instance.save()
#         self.assertIn(my_instance, functional_group.projects.all())
#
#     @tag('Project', 'models', '12m')
#     def test_12m_default_funding_source(self):
#         # a `project` that is attached to a given `default_funding_source` should be accessible by the reverse name `projects2`
#         funding_source = FactoryFloor.FundingSourceFactory()
#         my_instance = self.instance
#         my_instance.default_funding_source = funding_source
#         my_instance.save()
#         self.assertIn(my_instance, funding_source.projects.all())
#
#     @tag('Project', 'models', 'm2m')
#     def test_m2m_tags(self):
#         # a `project` that is attached to a given `tags` should be accessible by the m2m field name `tags`
#         tags = models.Tag.objects.all()[faker.random_int(0, models.Tag.objects.count() - 1)]
#         tags = FactoryFloor.TagFactory()
#         self.instance.tags.add(tags)
#         self.assertEqual(self.instance.tags.count(), 1)
#         self.assertIn(tags, self.instance.tags.all())
#
#     @tag('Project', 'models', 'm2m')
#     def test_m2m_references(self):
#         # a `project` that is attached to a given `references` should be accessible by the m2m field name `references`
#         references = models.Tag.objects.all()[faker.random_int(0, models.Tag.objects.count() - 1)]
#         references = CitationFactory()
#         self.instance.references.add(references)
#         self.assertEqual(self.instance.references.count(), 1)
#         self.assertIn(references, self.instance.references.all())
#
#     @tag('Project', 'models', 'm2m')
#     def test_m2m_funding_sources(self):
#         # a `project` that is attached to a given `funding_sources` should be accessible by the m2m field name `funding_sources`
#         funding_sources = models.Tag.objects.all()[faker.random_int(0, models.Tag.objects.count() - 1)]
#         funding_sources = FactoryFloor.FundingSourceFactory()
#         self.instance.funding_sources.add(funding_sources)
#         self.assertEqual(self.instance.funding_sources.count(), 1)
#         self.assertIn(funding_sources, self.instance.funding_sources.all())
#
#     @tag('Project', 'models', 'm2m')
#     def test_m2m_lead_staff(self):
#         # a `project` that is attached to a given `lead_staff` should be accessible by the m2m field name `lead_staff`
#         lead_staff = models.Tag.objects.all()[faker.random_int(0, models.Tag.objects.count() - 1)]
#         lead_staff = FactoryFloor.LeadStaffFactory()
#         self.instance.lead_staff.add(lead_staff)
#         self.assertEqual(self.instance.lead_staff.count(), 1)
#         self.assertIn(lead_staff, self.instance.lead_staff.all())
#
#
# class TestProjectYearModel(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.ProjectYearFactory()
#         self.instance = models.ProjectYear.objects.all()[faker.random_int(0, models.ProjectYear.objects.count() - 1)]
#
#     @tag('ProjectYear', 'models', 'fields')
#     def test_fields(self):
#         fields_to_check = ["name", ]
#         self.assert_has_fields(models.ProjectYear, fields_to_check)
#
#     @tag('ProjectYear', 'models', 'props')
#     def test_props(self):
#         self.assert_has_props(models.ProjectYear, ["tname"])
#
#     @tag('ProjectYear', 'models', 'inheritance')
#     def test_inheritance(self):
#         self.assert_inheritance(type(self.instance), shared_models.AbstractModel)
#
#     @tag('ProjectYear', 'models', '12m')
#     def test_12m_project(self):
#         # a `project_year` that is attached to a given `project` should be accessible by the reverse name `project_years`
#         project = FactoryFloor.ProjectFactory()
#         my_instance = self.instance
#         my_instance.project = project
#         my_instance.save()
#         self.assertIn(my_instance, project.years.all())
#
#     @tag('ProjectYear', 'models', '12m')
#     def test_12m_fiscal_year(self):
#         # a `project_year` that is attached to a given `project` should be accessible by the reverse name `project_years`
#         fiscal_year = shared_models.FiscalYear.objects.all()[faker.random_int(0, shared_models.FiscalYear.objects.count() - 1)]
#         my_instance = self.instance
#         my_instance.fiscal_year = fiscal_year
#         my_instance.save()
#         self.assertIn(my_instance, fiscal_year.project_year_set.all())
#
#     @tag('ProjectYear', 'models', 'm2m')
#     def test_m2m_existing_project_codes(self):
#         # a `project_year` that is attached to a given `existing_project_codes` should be accessible by the m2m field name `existing_project_codess`
#         existing_project_codes = ProjectFactory()
#         self.instance.existing_project_codess.add(existing_project_codes)
#         self.assertEqual(self.instance.existing_project_codess.count(), 1)
#         self.assertIn(existing_project_codes, self.instance.existing_project_codess.all())
#
#     @tag('ProjectYear', 'models', 'unique_together')
#     def test_unique_together(self):
#         expected_unique_together = (('project', 'fiscal_year'),)
#         actual_unique_together = models.ProjectYear._meta.unique_together
#         self.assertEqual(expected_unique_together, actual_unique_together)
#
#     @tag('ProjectYear', 'models', 'choices')
#     def test_choices_status(self):
#         actual_choices = [
#         (1, "Draft"),
#         (2, "Submitted"),
#         (3, "Reviewed"),
#         (4, "Approved"),
#         (5, "Not Approved"),
#         (9, "Cancelled"),
#     ]
#         expected_choices = [field.choices for field in models.ProjectYear._meta.fields if field.name == "status"][0]
#         self.assertEqual(actual_choices, expected_choices)
#
#     @tag('ProjectYear', 'models', 'mandatory_fields')
#     def test_mandatory_fields(self):
#         fields_to_check = ['project','start_date']
#         self.assert_mandatory_fields(models.ProjectYear, fields_to_check)