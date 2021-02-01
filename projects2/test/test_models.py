from datetime import datetime

from django.test import tag
from django.utils import timezone
from django.utils.translation import gettext as _
from faker import Factory

from shared_models import models as shared_models
from shared_models.test.SharedModelsFactoryFloor import CitationFactory, ProjectFactory, UserFactory
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


class TestProjectModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectFactory()

    @tag('Project', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'section',
            'title',
            'activity_type',
            'functional_group',
            'default_funding_source',
            'overview',
            'is_hidden',
            'organization',
            'species_involved',
            'team_description',
            'rationale',
            'experimental_protocol',
            'client_information',
            'second_priority',
            'objectives',
            'innovation',
            'other_funding',
            'start_date',
            'end_date',
            'staff_search_field',
            'created_at',
            'updated_at',
            'modified_by',
        ]
        self.assert_has_fields(models.Project, fields_to_check)

    @tag('Project', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Project, [
            "metadata",
            "dates",
            "has_unsubmitted_years",
            "region",
            "division",
            "overview_html",
            "objectives_html",
            "innovation_html",
            "other_funding_html",
            "team_description_html",
            "rationale_html",
            "experimental_protocol_html",
            "client_information_html",
            "get_funding_sources",
            "is_acrdp",
            "is_csrf",
            "fiscal_years",
        ])

    @tag('Project', 'models', '12m')
    def test_12m_section(self):
        # a `project` that is attached to a given `section` should be accessible by the reverse name `projects2`
        section = FactoryFloor.SectionFactory()
        my_instance = self.instance
        my_instance.section = section
        my_instance.save()
        self.assertIn(my_instance, section.projects2.all())

    @tag('Project', 'models', '12m')
    def test_12m_functional_group(self):
        # a `project` that is attached to a given `functional_group` should be accessible by the reverse name `projects2`
        functional_group = FactoryFloor.FunctionalGroupFactory()
        my_instance = self.instance
        my_instance.functional_group = functional_group
        my_instance.save()
        self.assertIn(my_instance, functional_group.projects.all())

    @tag('Project', 'models', '12m')
    def test_12m_default_funding_source(self):
        # a `project` that is attached to a given `default_funding_source` should be accessible by the reverse name `projects2`
        funding_source = FactoryFloor.FundingSourceFactory()
        my_instance = self.instance
        my_instance.default_funding_source = funding_source
        my_instance.save()
        self.assertIn(my_instance, funding_source.projects.all())

    @tag('Project', 'models', 'm2m')
    def test_m2m_tags(self):
        # a `project` that is attached to a given `tags` should be accessible by the m2m field name `tags`
        tags = FactoryFloor.TagFactory()
        self.instance.tags.add(tags)
        self.assertEqual(self.instance.tags.count(), 1)
        self.assertIn(tags, self.instance.tags.all())

    @tag('Project', 'models', 'm2m')
    def test_m2m_references(self):
        # a `project` that is attached to a given `references` should be accessible by the m2m field name `references`
        references = CitationFactory()
        self.instance.references.add(references)
        self.assertEqual(self.instance.references.count(), 1)
        self.assertIn(references, self.instance.references.all())

    @tag('Project', 'models', 'm2m')
    def test_m2m_funding_sources(self):
        # a `project` that is attached to a given `funding_sources` should be accessible by the m2m field name `funding_sources`
        funding_sources = FactoryFloor.FundingSourceFactory()
        self.instance.funding_sources.add(funding_sources)
        self.assertEqual(self.instance.funding_sources.count(), 1)
        self.assertIn(funding_sources, self.instance.funding_sources.all())

    @tag('Project', 'models', 'm2m')
    def test_m2m_lead_staff(self):
        # a `project` that is attached to a given `lead_staff` should be accessible by the m2m field name `lead_staff`
        lead_staff = FactoryFloor.LeadStaffFactory()
        self.instance.lead_staff.add(lead_staff)
        self.assertEqual(self.instance.lead_staff.count(), 1)
        self.assertIn(lead_staff, self.instance.lead_staff.all())


class TestProjectYearModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProjectYearFactory()

    @tag('ProjectYear', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'status',
            'project',
            'start_date',
            'end_date',
            'priorities',
            'deliverables',
            'requires_specialized_equipment',
            'technical_service_needs',
            'mobilization_needs',
            'has_field_component',
            'vehicle_needs',
            'ship_needs',
            'coip_reference_id',
            'instrumentation',
            'owner_of_instrumentation',
            'requires_field_staff',
            'field_staff_needs',
            'has_data_component',
            'data_collected',
            'data_products',
            'open_data_eligible',
            'data_storage_plan',
            'data_management_needs',
            'has_lab_component',
            'requires_abl_services',
            'requires_lab_space',
            'requires_other_lab_support',
            'other_lab_support_needs',
            'it_needs',
            'additional_notes',
            'responsibility_center',
            'allotment_code',
            'submitted',
            'administrative_notes',
            'created_at',
            'updated_at',
            'modified_by',
            'fiscal_year',
            'coding',
        ]
        self.assert_has_fields(models.ProjectYear, fields_to_check)

    @tag('ProjectYear', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.ProjectYear, [
            "update_modified_by",
            "metadata",
            "costs",
            "add_all_om_costs",
            "clear_empty_om_costs",
            "dates",
            "deliverables_html",
            "priorities_html",
            "get_project_leads_as_users",
            "get_coding",
            "get_funding_sources",
            "formatted_status",
            "submit",
            "unsubmit",
            "allocated_budget",
            "review_score_percentage",
            "review_score_fraction",
        ])

    @tag('ProjectYear', 'models', '12m')
    def test_12m_project(self):
        # a `project_year` that is attached to a given `project` should be accessible by the reverse name `project_years`
        project = FactoryFloor.ProjectFactory()
        my_instance = self.instance
        my_instance.project = project
        my_instance.save()
        self.assertIn(my_instance, project.years.all())

    @tag('ProjectYear', 'models', '12m')
    def test_12m_fiscal_year(self):
        # a `project_year` that is attached to a given `project` should be accessible by the reverse name `project_years`
        fiscal_year = shared_models.FiscalYear.objects.all()[faker.random_int(0, shared_models.FiscalYear.objects.count() - 1)]
        my_instance = self.instance
        my_instance.start_date = datetime(year=fiscal_year.id - 1, month=4, day=1, tzinfo=timezone.get_current_timezone())
        my_instance.save()
        self.assertIn(my_instance, fiscal_year.projectyear_set.all())

    @tag('ProjectYear', 'models', 'm2m')
    def test_m2m_existing_project_codes(self):
        # a `project_year` that is attached to a given `existing_project_codes` should be accessible by the m2m field name `existing_project_codes`
        existing_project_codes = ProjectFactory()
        self.instance.existing_project_codes.add(existing_project_codes)
        self.assertEqual(self.instance.existing_project_codes.count(), 1)
        self.assertIn(existing_project_codes, self.instance.existing_project_codes.all())

    @tag('ProjectYear', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('project', 'fiscal_year'),)
        actual_unique_together = models.ProjectYear._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('ProjectYear', 'models', 'choices')
    def test_choices_status(self):
        actual_choices = [
            (1, "Draft"),
            (2, "Submitted"),
            (3, "Reviewed"),
            (4, "Approved"),
            (5, "Not Approved"),
            (9, "Cancelled"),
        ]
        expected_choices = [field.choices for field in models.ProjectYear._meta.fields if field.name == "status"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('ProjectYear', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['project', 'start_date', 'status']
        self.assert_mandatory_fields(models.ProjectYear, fields_to_check)


class TestGenericCostModel(CommonTest):
    def setUp(self):
        super().setUp()

    @tag('GenericCost', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ['project_year', 'funding_source', "amount", ]
        self.assert_has_fields(models.GenericCost, fields_to_check)

    @tag('GenericCost', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['project_year', 'funding_source', ]
        self.assert_mandatory_fields(models.GenericCost, fields_to_check)


class TestEmployeeTypeModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.EmployeeType.objects.all()[faker.random_int(0, models.EmployeeType.objects.count() - 1)]

    @tag('EmployeeType', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["cost_type", "exclude_from_rollup"]
        self.assert_has_fields(models.EmployeeType, fields_to_check)

    @tag('EmployeeType', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), shared_models.SimpleLookup)

    @tag('EmployeeType', 'models', 'choices')
    def test_choices_cost_type(self):
        actual_choices = [
            (1, _("Salary")),
            (2, _("O&M")),
        ]
        expected_choices = [field.choices for field in models.EmployeeType._meta.fields if field.name == "cost_type"][0]
        self.assertEqual(actual_choices, expected_choices)


class TestStaffModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StaffFactory()

    @tag('Staff', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'employee_type',
            'is_lead',
            'user',
            'name',
            'level',
            'student_program',
            'duration_weeks',
            'overtime_hours',
            'overtime_description',
            'role',
            'expertise',
        ]
        self.assert_has_fields(models.Staff, fields_to_check)

    @tag('Staff', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Staff, [
            "smart_name",
        ])

    @tag('Staff', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), models.GenericCost)

    @tag('Staff', 'models', '12m')
    def test_12m_employee_type(self):
        # a `staff` that is attached to a given `employee_type` should be accessible by the reverse name `staff_set`
        employee_type = models.EmployeeType.objects.all()[faker.random_int(0, models.EmployeeType.objects.count() - 1)]
        my_instance = self.instance
        my_instance.employee_type = employee_type
        my_instance.save()
        self.assertIn(my_instance, employee_type.staff_set.all())

    @tag('Staff', 'models', '12m')
    def test_12m_user(self):
        # a `staff` that is attached to a given `user` should be accessible by the reverse name `staff_set`
        user = UserFactory()
        my_instance = self.instance
        my_instance.user = user
        my_instance.save()
        self.assertIn(my_instance, user.staff_instances2.all())

    @tag('Staff', 'models', '12m')
    def test_12m_level(self):
        # a `staff` that is attached to a given `level` should be accessible by the reverse name `staff_set`
        level = models.Level.objects.all()[faker.random_int(0, models.EmployeeType.objects.count() - 1)]
        my_instance = self.instance
        my_instance.level = level
        my_instance.save()
        self.assertIn(my_instance, level.staff_set.all())

    @tag('Staff', 'models', '12m')
    def test_12m_funding_source(self):
        # a `omcost` that is attached to a given `funding_source` should be accessible by the reverse name `omcost_set`
        funding_source = FactoryFloor.FundingSourceFactory()
        funding_source = models.FundingSource.objects.all()[faker.random_int(0, models.FundingSource.objects.count() - 1)]
        my_instance = self.instance
        my_instance.funding_source = funding_source
        my_instance.save()
        self.assertIn(my_instance, funding_source.staff_set.all())

    @tag('Staff', 'models', '12m')
    def test_12m_project_year(self):
        # a `omcost` that is attached to a given `project_year` should be accessible by the reverse name `omcost_set`
        project_year = FactoryFloor.ProjectYearFactory()
        my_instance = self.instance
        my_instance.project_year = project_year
        my_instance.save()
        self.assertIn(my_instance, project_year.staff_set.all())

    @tag('Staff', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('project_year', 'user'),)
        actual_unique_together = models.Staff._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('Staff', 'models', 'choices')
    def test_choices_student_program(self):
        actual_choices = [
            (1, "FSWEP"),
            (2, "Coop"),
        ]
        expected_choices = [field.choices for field in models.Staff._meta.fields if field.name == "student_program"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Staff', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['employee_type', ]
        self.assert_mandatory_fields(models.Staff, fields_to_check)


class TestOMCategoryModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.OMCategory.objects.all()[faker.random_int(0, models.OMCategory.objects.count() - 1)]

    @tag('OMCategory', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["name", 'nom', "group"]
        self.assert_has_fields(models.OMCategory, fields_to_check)

    @tag('OMCategory', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.OMCategory, ["tname"])

    @tag('OMCategory', 'models', 'choices')
    def test_choices_group(self):
        actual_choices = (
            (1, _("Travel")),
            (2, _("Equipment Purchase")),
            (3, _("Material and Supplies")),
            (4, _("Human Resources")),
            (5, _("Contracts, Leases, Services")),
            (6, _("Other")),
        )
        expected_choices = [field.choices for field in models.OMCategory._meta.fields if field.name == "group"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('OMCategory', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['group', ]
        self.assert_mandatory_fields(models.OMCategory, fields_to_check)


class TestOMCostModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OMCostFactory()

    @tag('OMCost', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["om_category", 'description']
        self.assert_has_fields(models.OMCost, fields_to_check)

    @tag('OMCost', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.OMCost, ["category_type"])

    @tag('OMCost', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), models.GenericCost)

    @tag('OMCost', 'models', '12m')
    def test_12m_funding_source(self):
        # a `omcost` that is attached to a given `funding_source` should be accessible by the reverse name `omcost_set`
        funding_source = FactoryFloor.FundingSourceFactory()
        funding_source = models.FundingSource.objects.all()[faker.random_int(0, models.FundingSource.objects.count() - 1)]
        my_instance = self.instance
        my_instance.funding_source = funding_source
        my_instance.save()
        self.assertIn(my_instance, funding_source.omcost_set.all())

    @tag('OMCost', 'models', '12m')
    def test_12m_project_year(self):
        # a `omcost` that is attached to a given `project_year` should be accessible by the reverse name `omcost_set`
        project_year = FactoryFloor.ProjectYearFactory()
        my_instance = self.instance
        my_instance.project_year = project_year
        my_instance.save()
        self.assertIn(my_instance, project_year.omcost_set.all())

    @tag('OMCost', 'models', '12m')
    def test_12m_om_category(self):
        # a `omcost` that is attached to a given `om_category` should be accessible by the reverse name `omcost_set`
        om_category = models.OMCategory.objects.all()[faker.random_int(0, models.OMCategory.objects.count() - 1)]
        my_instance = self.instance
        my_instance.om_category = om_category
        my_instance.save()
        self.assertIn(my_instance, om_category.om_costs.all())

    @tag('OMCost', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['om_category', ]
        self.assert_mandatory_fields(models.OMCost, fields_to_check)


class TestCapitalCostModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.CapitalCostFactory()

    @tag('CapitalCost', 'models', 'fields')
    def test_fields(self):
        fields_to_check = ["category", "description"]
        self.assert_has_fields(models.CapitalCost, fields_to_check)

    @tag('CapitalCost', 'models', 'inheritance')
    def test_inheritance(self):
        self.assert_inheritance(type(self.instance), models.GenericCost)

    @tag('CapitalCost', 'models', '12m')
    def test_12m_funding_source(self):
        # a `captialcost` that is attached to a given `funding_source` should be accessible by the reverse name `captialcost_set`
        funding_source = FactoryFloor.FundingSourceFactory()
        my_instance = self.instance
        my_instance.funding_source = funding_source
        my_instance.save()
        self.assertIn(my_instance, funding_source.capitalcost_set.all())

    @tag('CapitalCost', 'models', '12m')
    def test_12m_project_year(self):
        # a `capitalcost` that is attached to a given `project_year` should be accessible by the reverse name `capitalcost_set`
        project_year = FactoryFloor.ProjectYearFactory()
        my_instance = self.instance
        my_instance.project_year = project_year
        my_instance.save()
        self.assertIn(my_instance, project_year.capitalcost_set.all())

    @tag('CapitalCost', 'models', 'choices')
    def test_choices_category(self):
        actual_choices = (
            (1, _("IM / IT - computers, hardware")),
            (2, _("Lab Equipment")),
            (3, _("Field Equipment")),
            (4, _("Other")),
        )
        expected_choices = [field.choices for field in models.CapitalCost._meta.fields if field.name == "category"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('CapitalCost', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['category', ]
        self.assert_mandatory_fields(models.CapitalCost, fields_to_check)


class TestCollaborationModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.CollaborationFactory()

    @tag('Collaboration', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'project_year',
            'type',
            'new_or_existing',
            'organization',
            'people',
            'critical',
            'agreement_title',
            'gc_program',
            'amount',
            'notes',
        ]
        self.assert_has_fields(models.Collaboration, fields_to_check)

    @tag('Collaboration', 'models', '12m')
    def test_12m_project_year(self):
        # a `collaboration` that is attached to a given `project_year` should be accessible by the reverse name `collaborations`
        project_year = FactoryFloor.ProjectYearFactory()
        my_instance = self.instance
        my_instance.project_year = project_year
        my_instance.save()
        self.assertIn(my_instance, project_year.collaborations.all())

    @tag('Collaboration', 'models', 'choices')
    def test_choices_new_or_existing(self):
        actual_choices = [
            (1, _("New")),
            (2, _("Existing")),
        ]
        expected_choices = [field.choices for field in models.Collaboration._meta.fields if field.name == "new_or_existing"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Collaboration', 'models', 'choices')
    def test_choices_type(self):
        actual_choices = (
            (1, _("External Collaborator")),
            (2, _("Grant & Contribution Agreement")),
            (3, _("Collaborative Agreement")),
        )
        expected_choices = [field.choices for field in models.Collaboration._meta.fields if field.name == "type"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Collaboration', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = [
            'project_year',
            'type',
            'new_or_existing',
        ]
        self.assert_mandatory_fields(models.Collaboration, fields_to_check)


class TestStatusReportModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StatusReportFactory()

    @tag('StatusReport', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'project_year',
            'status',
            'major_accomplishments',
            'major_issues',
            'target_completion_date',
            'rationale_for_modified_completion_date',
            'general_comment',
            'section_head_comment',
            'section_head_reviewed',
            'created_at',
            'updated_at',
            'modified_by',
        ]
        self.assert_has_fields(models.StatusReport, fields_to_check)

    @tag('StatusReport', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.StatusReport, [
            "metadata",
            "report_number",
            "major_accomplishments_html",
            "major_issues_html",
        ])

    @tag('StatusReport', 'models', '12m')
    def test_12m_project_year(self):
        # a `status_report` that is attached to a given `project_year` should be accessible by the reverse name `status_reports`
        project_year = FactoryFloor.ProjectYearFactory()
        my_instance = self.instance
        my_instance.project_year = project_year
        my_instance.save()
        self.assertIn(my_instance, project_year.reports.all())

    @tag('StatusReport', 'models', 'choices')
    def test_choices_status(self):
        actual_choices = (
            (3, _("On-track")),
            (4, _("Complete")),
            (5, _("Encountering issues")),
            (6, _("Aborted / cancelled")),
        )
        expected_choices = [field.choices for field in models.StatusReport._meta.fields if field.name == "status"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('StatusReport', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['project_year', 'status', ]
        self.assert_mandatory_fields(models.StatusReport, fields_to_check)


class TestReviewModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReviewFactory()

    @tag('Review', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'project_year',
            'operational_score',
            'operational_comment',
            'ecological_score',
            'ecological_comment',
            'scale_score',
            'scale_comment',
            'general_comment',
            'comments_for_staff',
            'approval_status',
            'approval_level',
            'allocated_budget',
            'approval_notification_email_sent',
            'review_notification_email_sent',
            'approver_comment',
            'created_at',
            'updated_at',
            'last_modified_by',
            'total_score',
        ]
        self.assert_has_fields(models.Review, fields_to_check)

    @tag('Review', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Review, [
            "metadata",
            "general_comment_html",
            "score_as_percent",
            "send_approval_email",
            "send_review_email",
            "score_html_template",
            "collaboration_score_html",
            "strategic_score_html",
            "operational_score_html",
            "ecological_score_html",
            "scale_score_html",
        ])

    @tag('Review', 'models', 'm2m')
    def test_m2m_modified_by(self):
        # a `review` that is attached to a given `user` should be accessible by the m2m field name `modified_by`
        user = FactoryFloor.UserFactory()
        self.instance.modified_by.add(user)
        self.assertEqual(self.instance.modified_by.count(), 1)
        self.assertIn(user, self.instance.modified_by.all())

    @tag('Review', 'models', '121')
    def test_12m_project_year(self):
        # a `review` that is attached to a given `project_year` should be accessible by the reverse name `reviews`
        project_year = FactoryFloor.ProjectYearFactory()
        my_instance = self.instance
        my_instance.project_year = project_year
        my_instance.save()
        self.assertEqual(my_instance, project_year.review)

    @tag('Review', 'models', 'choices')
    def test_choices_approval_scores(self):
        actual_choices = (
            (3, _("high")),
            (2, _("medium")),
            (1, _("low")),
        )
        expected_choices = [field.choices for field in models.Review._meta.fields if field.name == "collaboration_score"][0]
        self.assertEqual(actual_choices, expected_choices)
        expected_choices = [field.choices for field in models.Review._meta.fields if field.name == "strategic_score"][0]
        self.assertEqual(actual_choices, expected_choices)
        expected_choices = [field.choices for field in models.Review._meta.fields if field.name == "operational_score"][0]
        self.assertEqual(actual_choices, expected_choices)
        expected_choices = [field.choices for field in models.Review._meta.fields if field.name == "ecological_score"][0]
        self.assertEqual(actual_choices, expected_choices)
        expected_choices = [field.choices for field in models.Review._meta.fields if field.name == "scale_score"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Review', 'models', 'choices')
    def test_choices_approval_status(self):
        actual_choices = (
            (1, _("approved")),
            (0, _("not approved")),
            (9, _("cancelled")),
        )
        expected_choices = [field.choices for field in models.Review._meta.fields if field.name == "approval_status"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Review', 'models', 'choices')
    def test_choices_approval_level(self):
        actual_choices = (
            (1, _("Division-level")),
            (2, _("Branch-level")),
            (3, _("National")),
        )
        expected_choices = [field.choices for field in models.Review._meta.fields if field.name == "approval_level"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Review', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = [
            'project_year',
        ]
        self.assert_mandatory_fields(models.Review, fields_to_check)


class TestActivityModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ActivityFactory()

    @tag('Activity', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'project_year',
            'type',
            'name',
            'target_date',
            'description',
            'responsible_party',
            'risk_description',
            'impact',
            'likelihood',
            'risk_rating',
            'mitigation_measures',
        ]
        self.assert_has_fields(models.Activity, fields_to_check)

    @tag('Activity', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.Activity, ["latest_update"])

    @tag('Activity', 'models', '12m')
    def test_12m_project_year(self):
        # a `activity` that is attached to a given `project_year` should be accessible by the reverse name `activities`
        project_year = FactoryFloor.ProjectYearFactory()
        my_instance = self.instance
        my_instance.project_year = project_year
        my_instance.save()
        self.assertIn(my_instance, project_year.activities.all())

    @tag('Activity', 'models', 'choices')
    def test_choices_type(self):
        actual_choices = (
            (1, _("Milestone")),
            (2, _("Deliverable")),
        )
        expected_choices = [field.choices for field in models.Activity._meta.fields if field.name == "type"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Activity', 'models', 'choices')
    def test_choices_likelihood(self):
        actual_choices = (
            (1, _("1-Very unlikely")),
            (2, _("2-Unlikely")),
            (3, _("3-Low")),
            (4, _("4-Likely")),
            (5, _("5-Almost certain")),
        )
        expected_choices = [field.choices for field in models.Activity._meta.fields if field.name == "likelihood"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Activity', 'models', 'choices')
    def test_choices_impact(self):
        actual_choices = (
            (1, _("1-Negligible")),
            (2, _("2-Low")),
            (3, _("3-Medium")),
            (4, _("4-High")),
            (5, _("5-Extreme")),
        )
        expected_choices = [field.choices for field in models.Activity._meta.fields if field.name == "impact"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Activity', 'models', 'choices')
    def test_choices_risk_rating(self):
        actual_choices = (
            (None, "n/a"),
            (1, _("Low")),
            (2, _("Medium")),
            (3, _("High")),
        )
        expected_choices = [field.choices for field in models.Activity._meta.fields if field.name == "risk_rating"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('Activity', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['name', 'project_year', 'type', ]
        self.assert_mandatory_fields(models.Activity, fields_to_check)


class TestActivityUpdateModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ActivityUpdateFactory()
        self.instance = models.ActivityUpdate.objects.all()[faker.random_int(0, models.ActivityUpdate.objects.count() - 1)]

    @tag('ActivityUpdate', 'models', 'fields')
    def test_fields(self):
        fields_to_check = [
            'activity',
            'status_report',
            'status',
            'notes',
        ]
        self.assert_has_fields(models.ActivityUpdate, fields_to_check)

    @tag('ActivityUpdate', 'models', 'props')
    def test_props(self):
        self.assert_has_props(models.ActivityUpdate, ["notes_html"])

    @tag('ActivityUpdate', 'models', '12m')
    def test_12m_activity(self):
        # a `update` that is attached to a given `activity` should be accessible by the reverse name `updates`
        activity = FactoryFloor.ActivityFactory()
        my_instance = self.instance
        my_instance.activity = activity
        my_instance.save()
        self.assertIn(my_instance, activity.updates.all())

    @tag('ActivityUpdate', 'models', '12m')
    def test_12m_status_report(self):
        # a `update` that is attached to a given `status_report` should be accessible by the reverse name `updates`
        status_report = FactoryFloor.StatusReportFactory()
        my_instance = self.instance
        my_instance.status_report = status_report
        my_instance.save()
        self.assertIn(my_instance, status_report.updates.all())

    @tag('ActivityUpdate', 'models', 'unique_together')
    def test_unique_together(self):
        expected_unique_together = (('activity', 'status_report'),)
        actual_unique_together = models.ActivityUpdate._meta.unique_together
        self.assertEqual(expected_unique_together, actual_unique_together)

    @tag('ActivityUpdate', 'models', 'choices')
    def test_choices_status(self):
        actual_choices = (
            (7, _("In progress")),
            (8, _("Completed")),
            (9, _("Aborted / cancelled")),
        )
        expected_choices = [field.choices for field in models.ActivityUpdate._meta.fields if field.name == "status"][0]
        self.assertEqual(actual_choices, expected_choices)

    @tag('ActivityUpdate', 'models', 'mandatory_fields')
    def test_mandatory_fields(self):
        fields_to_check = ['status', 'status_report', 'activity', ]
        self.assert_mandatory_fields(models.ActivityUpdate, fields_to_check)
