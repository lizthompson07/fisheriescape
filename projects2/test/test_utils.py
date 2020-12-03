from datetime import datetime

from django.test import tag
from django.utils import timezone
from faker import Factory

from shared_models.test.SharedModelsFactoryFloor import SectionFactory
from . import FactoryFloor
from .. import models, utils
from ..test.common_tests import CommonProjectTest as CommonTest

faker = Factory.create()


class TestUtils(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres

    @tag("utils")
    def test_auth_utils(self):
        section = SectionFactory()
        rando = self.get_and_login_user()
        admin = self.get_and_login_user(in_group="projects_admin")
        section_head = section.head
        division_head = section.division.head
        branch_head = section.division.branch.head

        project = FactoryFloor.ProjectFactory()
        project_year1 = FactoryFloor.ProjectYearFactory(project=project)
        project_year2 = FactoryFloor.ProjectYearFactory(project=project)
        staff1a = FactoryFloor.LeadStaffFactory(project_year=project_year1)
        staff1b = FactoryFloor.StaffFactory(project_year=project_year1, is_lead=False)
        staff2a = FactoryFloor.LeadStaffFactory(project_year=project_year2)
        staff2b = FactoryFloor.StaffFactory(project_year=project_year2, is_lead=False)

        # is in projects admin group
        self.assertFalse(utils.in_projects_admin_group(rando))
        self.assertFalse(utils.in_projects_admin_group(section_head))
        self.assertTrue(utils.in_projects_admin_group(admin))

        # is manager
        self.assertFalse(utils.is_management(rando))
        self.assertFalse(utils.is_management(admin))
        self.assertTrue(utils.is_management(section_head))
        self.assertTrue(utils.is_management(division_head))
        self.assertTrue(utils.is_management(branch_head))

        # is manager or admin
        self.assertFalse(utils.is_admin_or_project_manager(rando, project))
        self.assertFalse(utils.is_admin_or_project_manager(section_head, project))
        self.assertTrue(utils.is_admin_or_project_manager(admin, project))
        self.assertTrue(utils.is_admin_or_project_manager(project.section.head, project))
        self.assertTrue(utils.is_admin_or_project_manager(project.section.division.head, project))
        self.assertTrue(utils.is_admin_or_project_manager(project.section.division.branch.head, project))

        # is section head
        self.assertFalse(utils.is_section_head(section_head, project))
        self.assertFalse(utils.is_section_head(project.section.division.head, project))
        self.assertFalse(utils.is_section_head(project.section.division.branch.head, project))
        self.assertTrue(utils.is_section_head(project.section.head, project))

        # is_division_manager
        self.assertFalse(utils.is_division_manager(division_head, project))
        self.assertFalse(utils.is_division_manager(project.section.head, project))
        self.assertFalse(utils.is_division_manager(project.section.division.branch.head, project))
        self.assertTrue(utils.is_division_manager(project.section.division.head, project))

        # is_rds
        self.assertFalse(utils.is_rds(branch_head, project))
        self.assertFalse(utils.is_rds(project.section.head, project))
        self.assertFalse(utils.is_rds(project.section.division.head, project))
        self.assertTrue(utils.is_rds(project.section.division.branch.head, project))
        self.assertTrue(utils.is_rds(branch_head))

        # is_project_lead
        # first with project id
        self.assertFalse(utils.is_project_lead(section_head, project_id=project.id))
        self.assertFalse(utils.is_project_lead(admin, project_id=project.id))
        self.assertFalse(utils.is_project_lead(rando, project_id=project.id))
        self.assertFalse(utils.is_project_lead(staff1b.user, project_id=project.id))
        self.assertFalse(utils.is_project_lead(staff2b.user, project_id=project.id))
        self.assertTrue(utils.is_project_lead(staff1a.user, project_id=project.id))
        self.assertTrue(utils.is_project_lead(staff2a.user, project_id=project.id))

        # first with project id
        self.assertFalse(utils.is_project_lead(section_head, project_year_id=project_year1.id))
        self.assertFalse(utils.is_project_lead(admin, project_year_id=project_year1.id))
        self.assertFalse(utils.is_project_lead(rando, project_year_id=project_year1.id))
        self.assertFalse(utils.is_project_lead(staff1b.user, project_year_id=project_year1.id))
        self.assertFalse(utils.is_project_lead(staff2b.user, project_year_id=project_year1.id))
        self.assertTrue(utils.is_project_lead(staff1a.user, project_year_id=project_year1.id))
        self.assertTrue(utils.is_project_lead(staff2a.user, project_year_id=project_year1.id))

        # can_modify_project
        # first make sure the default is not to return bool statement
        self.assertIsInstance(utils.can_modify_project(rando, project.id), bool)
        self.assertIsInstance(utils.can_modify_project(rando, project.id, return_as_dict=True), dict)

        self.assertFalse(utils.can_modify_project(rando, project.id))
        self.assertFalse(utils.can_modify_project(section_head, project.id))
        self.assertFalse(utils.can_modify_project(division_head, project.id))
        self.assertFalse(utils.can_modify_project(branch_head, project.id))
        self.assertFalse(utils.can_modify_project(staff1b.user, project.id))
        self.assertFalse(utils.can_modify_project(staff2b.user, project.id))

        self.assertTrue(utils.can_modify_project(admin, project.id))
        self.assertTrue(utils.can_modify_project(project.section.head, project.id))
        self.assertTrue(utils.can_modify_project(project.section.division.head, project.id))
        self.assertTrue(utils.can_modify_project(project.section.division.branch.head, project.id))
        self.assertTrue(utils.can_modify_project(staff1a.user, project.id))
        self.assertTrue(utils.can_modify_project(staff2a.user, project.id))

        # if we delete all staff, then anyone should be allowed to modify
        models.Staff.objects.filter(project_year__project=project, is_lead=True).delete()
        self.assertTrue(utils.can_modify_project(rando, project.id))

    @tag("utils")
    def test_get_manageable_sections(self):
        project1 = FactoryFloor.ProjectFactory()
        project2 = FactoryFloor.ProjectFactory()
        section1 = project1.section
        section2 = project2.section
        section_head = section1.head
        division_head = section1.division.head
        branch_head = section1.division.branch.head
        rando = self.get_and_login_user()
        admin = self.get_and_login_user(in_group="projects_admin")

        self.assertIn(section1, utils.get_manageable_sections(section_head))
        self.assertIn(section1, utils.get_manageable_sections(division_head))
        self.assertIn(section1, utils.get_manageable_sections(branch_head))
        self.assertIn(section1, utils.get_manageable_sections(admin))
        self.assertIn(section2, utils.get_manageable_sections(admin))

        self.assertNotIn(section2, utils.get_manageable_sections(section_head))
        self.assertNotIn(section2, utils.get_manageable_sections(division_head))
        self.assertNotIn(section2, utils.get_manageable_sections(branch_head))
        self.assertNotIn(section1, utils.get_manageable_sections(rando))
        self.assertNotIn(section2, utils.get_manageable_sections(rando))

    @tag("utils")
    def test_get_user_fte_breakdown(self):
        rando = self.get_and_login_user()
        start_date = datetime(year=2020, month=4, day=1, tzinfo=timezone.get_current_timezone())
        project_year1 = FactoryFloor.ProjectYearFactory(start_date=start_date, status=1)
        project_year2 = FactoryFloor.ProjectYearFactory(start_date=start_date, status=2)
        project_year3 = FactoryFloor.ProjectYearFactory(start_date=start_date, status=3)
        project_year4 = FactoryFloor.ProjectYearFactory(start_date=start_date, status=4)

        staff1 = FactoryFloor.StaffFactory(user=rando, project_year=project_year1, duration_weeks=10)
        staff2 = FactoryFloor.StaffFactory(user=rando, project_year=project_year2, duration_weeks=20)
        staff3 = FactoryFloor.StaffFactory(user=rando, project_year=project_year3, duration_weeks=30)
        staff4 = FactoryFloor.StaffFactory(user=rando, project_year=project_year4, duration_weeks=40)

        # get the data
        data = utils.get_user_fte_breakdown(rando, 2021)

        self.assertEqual(data["name"], f"{rando.last_name}, {rando.first_name}")
        self.assertEqual(data["fiscal_year"], "2020-2021")
        self.assertEqual(data["draft"], 10)
        self.assertEqual(data["submitted_unapproved"], 50)
        self.assertEqual(data["approved"], 40)

    @tag("utils")
    def test_financial_summaries(self):
        project = FactoryFloor.ProjectFactory()
        project_year1 = FactoryFloor.ProjectYearFactory(project=project)
        project_year2 = FactoryFloor.ProjectYearFactory(project=project)

        # let's deal with one funding source first
        omcost = FactoryFloor.OMCostFactory(project_year=project_year1, amount=1000)  # om
        funding_source = omcost.funding_source
        FactoryFloor.CapitalCostFactory(project_year=project_year1, funding_source=funding_source, amount=2000)  # capital
        FactoryFloor.StudentStaffFactory(project_year=project_year1, funding_source=funding_source, amount=3000)  # om
        FactoryFloor.StaffFactory(project_year=project_year1, funding_source=funding_source, amount=4000, employee_type_id=2)  # salary

        data = utils.financial_project_year_summary_data(project_year1)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["type"], funding_source.get_funding_source_type_display())
        self.assertEqual(data[0]["name"], str(funding_source))
        self.assertEqual(data[0]["salary"], 4000)
        self.assertEqual(data[0]["om"], 4000)
        self.assertEqual(data[0]["capital"], 2000)
        self.assertEqual(data[0]["total"], 10000)

        # now we add a second funding source
        omcost = FactoryFloor.OMCostFactory(project_year=project_year1, amount=1000)
        funding_source2 = omcost.funding_source
        data = utils.financial_project_year_summary_data(project_year1)
        self.assertEqual(len(data), 2)

        # now let's do everything again to test out to project-wide function

        # let's deal with one funding source first
        FactoryFloor.OMCostFactory(project_year=project_year2, amount=1000, funding_source=funding_source)  # om
        FactoryFloor.CapitalCostFactory(project_year=project_year2, funding_source=funding_source, amount=2000)  # capital
        FactoryFloor.StudentStaffFactory(project_year=project_year2, funding_source=funding_source, amount=3000)  # om
        FactoryFloor.StaffFactory(project_year=project_year2, funding_source=funding_source, amount=4000, employee_type_id=2)  # salary
        FactoryFloor.OMCostFactory(project_year=project_year2, amount=1000, funding_source=funding_source2)

        data = utils.financial_project_summary_data(project)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["type"], funding_source.get_funding_source_type_display())
        self.assertEqual(data[0]["name"], str(funding_source))
        self.assertEqual(data[0]["salary"], 8000)
        self.assertEqual(data[0]["om"], 8000)
        self.assertEqual(data[0]["capital"], 4000)
        self.assertEqual(data[0]["total"], 20000)


