from django.test import TestCase, Client, tag
from django.utils.translation import activate
from django.urls import reverse_lazy
from django.contrib.auth.models import User, Group

from projects import views, models
from shared_models import models as shared_models


# ======================================================================#
# It is expected that a 'test' database has been created to run these tests
# I do this by copying my db configuration variables for 'default' in settings.py
# and calling it 'default-test' and adding "test_" to the beginning of the
# database name so 'glf_sci_site' becomes 'test_glf_sci_site'
#
# Then manually run the migrations to create the test db
#   > python manage.py migrate --database=default-test
#
# To run all unit test:
#   > python manage.py test --keepdb -v 2 projects.tests
#
# To run tagged unit test, 'function' test for example:
#   > python manage.py test --keepdb -v 2 --tag function projects.tests
#
# It takes a long time for the test runner to build the database, so make
# sure to use the --keepdb option. Otherwise the test runner will destroy
# the test database at the end of the run and attempt to create a new test
# database the next time the tests are run.
#
# No need to worry if you forget to create a default-test database. default
# behaviour of manage.py test is to create test_[db name] even without modifying
# the settings.py file.
#
# the -v 2 option sets the level of verbosity, if you don't use it nothing
# gets printed until all tests have run. Using level to gives you the test name
# and if it was successful, error or fail
# ======================================================================#


# This class sets up the common element used in all view testing
class CommonTest(TestCase):
    client_class = Client  # <== client object is used to simulate a connection

    # url of the expect template a view will be testing
    view_url = None

    # template the view is expected to be using
    expected_template = None

    # url of the expected address a user will be redirected to if not logged in
    login_url_en = None

    # password used only with creating users for testing
    test_password = 'it5me_mari0!'

    # an account with regular user privileges
    regular_user = None

    # an account with manager privileges
    branch_user = None

    fy = None

    program = None

    abase_funding = None
    bbase_funding = None
    cbase_funding = None

    # setup common variables used in all testing.
    # classes extending CommonTest should override variables above that are set to None
    # unless those variables are set in this setUp method below
    def setUp(self):
        super().setUp()

        # create programs for program testing.
        self.program = models.Program2(is_core=True)
        self.program.save()

        # The IPSProjectList Expects funding models for a, b and c based funding to
        # exist
        self.abase_funding = models.FundingSource(id=1, name='abase', color='blue')
        self.abase_funding.save()

        self.bbase_funding = models.FundingSource(id=2, name='bbase', color='green')
        self.bbase_funding.save()

        self.cbase_funding = models.FundingSource(id=3, name='cbase', color='red')
        self.cbase_funding.save()

        # create the project admin group used for access testing.
        self.projects_admin_group = Group(name='projects_admin')
        self.projects_admin_group.save()

        # Create the users for access testing at various levels
        self.regular_user = User.objects.create_user(username="Regular", first_name="Joe", last_name="Average",
                                                     email="Average.Joe@dfo-mpo.gc.ca", password=self.test_password)
        self.regular_user.save()

        self.region_user = User.objects.create_user(username="Region", first_name="Slam", last_name="Bowser",
                                                    email="Bowser.Slam@dfo-mpo.gc.ca", password=self.test_password)
        self.region_user.save()

        self.branch_user = User.objects.create_user(username="Branch", first_name="Mario", last_name="Itsme",
                                                    email="Itsme.Mario@dfo-mpo.gc.ca", password=self.test_password)
        self.branch_user.save()

        self.division_user = User.objects.create_user(username="Division", first_name="Stool", last_name="Toad",
                                                      email="Toad.Stool@dfo-mpo.gc.ca", password=self.test_password)
        self.division_user.save()

        self.section_user = User.objects.create_user(username="Section", first_name="Peach", last_name="Princess",
                                                     email="Princess.Peach@dfo-mpo.gc.ca", password=self.test_password)
        self.section_user.save()

        self.admin_user = User.objects.create_superuser(username="Admin", first_name="Like", last_name="God",
                                                        email="God.Like@dfo-mpo.gc.ca", password=self.test_password)
        self.admin_user.save()

        self.admin_user.groups.add(self.projects_admin_group)
        self.admin_user.save()

    # This contains a "general" organizational structure, don't modify it here unless adding a test
    # that's common to all classes extending the CommonTest class. Instead, override it in the
    # extending class to add or change it.
    #
    # Call this method right after super().setUp() in the extending classes setUp() super method
    def create_org_structure(self):
        # create branch, division, section and add managers
        self.region_1 = shared_models.Region(name="region 1", abbrev="reg", head=self.region_user)
        self.region_1.save()

        self.branch_11 = shared_models.Branch(name="Region 1 Branch 1", abbrev="bra", head=self.branch_user,
                                              region=self.region_1)
        self.branch_11.save()

        self.division_111 = shared_models.Division(name="Region 1 Branch 1 Division 1", abbrev="div",
                                                   head=self.division_user,
                                                   branch=self.branch_11)
        self.division_111.save()

        self.section_1111 = shared_models.Section(name="Region 1 Branch 1 Division 1 Section 1", abbrev="sec",
                                                  head=self.section_user,
                                                  division=self.division_111)
        self.section_1111.save()

    # called whe projects need to be created for testing
    def create_projects(self):
        project_list = dict()

        prev_fy = shared_models.FiscalYear(full="2018-2019", short="18-19")
        prev_fy.save()

        fake_section = shared_models.Section(name="fakey fake section", division=self.division_111)
        fake_section.save()

        # this fiscal, and submitted, and approved. Project 4 is used to test order_by(id)
        project_list["project_4"] = models.Project(year=self.fy, project_title="Project 4", section=self.section_1111,
                                                   submitted=True, section_head_approved=True)
        project_list["project_4"].save()
        project_list["project_4"].programs.set([self.program])

        # this fiscal, and submitted, and approved
        project_list["project_1"] = models.Project(year=self.fy, project_title="Project 1", section=self.section_1111,
                                                   submitted=True, section_head_approved=True)
        project_list["project_1"].save()
        project_list["project_1"].programs.set([self.program])

        # submitted, but not approved
        project_list["project_2"] = models.Project(year=self.fy, project_title="Project 2", section=self.section_1111,
                                                   submitted=True, section_head_approved=False)
        project_list["project_2"].save()
        project_list["project_2"].programs.set([self.program])

        # submitted and approved, but a different fiscal year
        project_list["project_3"] = models.Project(year=prev_fy, project_title="Project 3", section=self.section_1111,
                                                   submitted=True, section_head_approved=True)
        project_list["project_3"].save()
        project_list["project_3"].programs.set([self.program])

        # this fiscal, and submitted, and approved
        project_list["project_5"] = models.Project(year=self.fy, project_title="Project 5", section=fake_section,
                                                   submitted=True, section_head_approved=True)
        project_list["project_5"].save()
        project_list["project_5"].programs.set([self.program])

        return project_list

    # create staff and add them to projects for funding testing
    def create_staff(self):
        staff_list = dict()

        et_sal = models.EmployeeType(name="Sal", cost_type=1)
        et_sal.save()

        et_om = models.EmployeeType(name="O&M", cost_type=2)
        et_om.save()

        level = models.Level(name="level 1")
        level.save()

        staff_list['projects'] = project_list = self.create_projects()

        # this guy needs a vacation ( 0_o)
        staff_list["staff_1"] = models.Staff(project=project_list['project_1'],
                                             employee_type=et_sal,
                                             funding_source=self.abase_funding,
                                             user=self.regular_user,
                                             level=level,
                                             overtime_hours=1005.25,
                                             cost=925.5)
        staff_list["staff_1"].save()

        staff_list["staff_4"] = models.Staff(project=project_list['project_4'],
                                             employee_type=et_sal,
                                             funding_source=self.cbase_funding,
                                             user=self.regular_user,
                                             level=level,
                                             overtime_hours=205.25,
                                             cost=525.5)
        staff_list["staff_4"].save()

        staff_list["staff_2"] = models.Staff(project=project_list['project_1'],
                                             employee_type=et_om,
                                             funding_source=self.bbase_funding,
                                             user=self.division_user,
                                             level=level,
                                             overtime_hours=0.25,
                                             cost=10.5)
        staff_list["staff_2"].save()

        staff_list["staff_3"] = models.Staff(project=project_list['project_4'],
                                             employee_type=et_sal,
                                             funding_source=self.cbase_funding,
                                             user=self.section_user,
                                             level=level,
                                             overtime_hours=1.25,
                                             cost=110.5)
        staff_list["staff_3"].save()
        return staff_list


class TestFunctions(CommonTest):

    def setUp(self):
        super().setUp()
        super().create_org_structure()

    # == in_projects_admin_group is a simple function that
    # checks if a user belongs to the project_admin group ==

    # test that a regular user is not in the admin group
    @tag('functions', 'access')
    def test_in_projects_admin_group_regular_user(self):
        self.assertFalse(views.in_projects_admin_group(self.regular_user), "user should not be in admin group")

    # test that a manager is not in the admin group
    @tag('functions', 'access')
    def test_in_projects_admin_group_manager_user(self):
        self.assertFalse(views.in_projects_admin_group(self.branch_user), "Manager should not be in admin group")

    # test that an admin is in the admin group
    @tag('functions', 'access')
    def test_in_projects_admin_group_admin_user(self):
        self.assertTrue(views.in_projects_admin_group(self.admin_user), "Admin should be in admin group")

    # == is_management_or_admin checks if a user belongs to
    # the project_admin group or
    # is a Section head or
    # is a Division head or
    # is a Branch head
    # ==

    # test that a regular user is not in the group
    @tag('functions', 'access')
    def test_is_management_or_admin_regular_user(self):
        self.assertFalse(views.is_management_or_admin(self.regular_user), "user should not be in any group")

    # test that an admin user is in the group
    @tag('functions', 'access')
    def test_is_management_or_admin_admin_user(self):
        self.assertTrue(views.is_management_or_admin(self.admin_user), "user should be in the admin group")

    # test that a section user is in the group
    @tag('functions', 'access')
    def test_is_management_or_admin_section_user(self):
        self.assertTrue(views.is_management_or_admin(self.section_user), "user should be a section head")

    # test that a division user is in the group
    @tag('functions', 'access')
    def test_is_management_or_admin_division_user(self):
        self.assertTrue(views.is_management_or_admin(self.division_user), "user should a division head")

    # test that a branch user is in the group
    @tag('functions', 'access')
    def test_is_management_or_admin_branch_user(self):
        self.assertTrue(views.is_management_or_admin(self.branch_user), "user should branch head")


class TestIPSProgramList(CommonTest):
    program2 = None

    def setUp(self):
        super().setUp()  # <== Make sure to call the parent class' setUp method
        self.create_org_structure()

        self.fy = shared_models.FiscalYear(full="2019-2020", short="19-20")
        self.fy.save()

        # setup common variables used in tests for this view
        self.view_url = reverse_lazy("projects:ips_program_list", args=[self.region_1.pk, self.fy.pk])
        self.expected_template = 'projects/ips_program_list.html'

        expected_url = '/projects/regional-meeting/region/' + str(self.region_1.pk) + \
                       '/programs-by-section/' + str(self.fy.pk) + '/'

        self.expected_url_en = '/en' + expected_url
        self.login_url_en = '/accounts/login_required/?next=' + self.expected_url_en

        self.expected_url_fr = '/fr' + expected_url
        self.login_url_fr = '/accounts/login_required/?next=' + self.expected_url_fr

    def create_org_structure(self):
        super().create_org_structure()

        self.section_1112 = shared_models.Section(name="Region 1 Branch 1 Division 1 Section 2", abbrev="sec",
                                                  head=self.section_user,
                                                  division=self.division_111)
        self.section_1112.save()

        self.division_112 = shared_models.Division(name="Region 1 Branch 1 Division 2", abbrev="div",
                                                   head=self.division_user,
                                                   branch=self.branch_11)
        self.division_112.save()

        self.section_1121 = shared_models.Section(name="Region 1 Branch 1 Division 2 Section 1", abbrev="sec",
                                                  head=self.section_user,
                                                  division=self.division_112)
        self.section_1121.save()

        self.section_1122 = shared_models.Section(name="Region 1 Branch 1 Division 2 Section 2", abbrev="sec",
                                                  head=self.section_user,
                                                  division=self.division_112)
        self.section_1122.save()

    def create_projects(self):
        project_list = super().create_projects()

        self.program2 = models.Program2(is_core=False)
        self.program2.save()

        # add a project and program to another division / section
        project_list["project_6"] = models.Project(year=self.fy, project_title="Project 6", section=self.section_1122,
                                                   submitted=True, section_head_approved=True)
        project_list["project_6"].save()
        project_list["project_6"].programs.set([self.program2])

        return project_list

    def create_staff(self):
        staff_list = super().create_staff()

        et_sal = models.EmployeeType(name="Sal", cost_type=1)
        et_sal.save()

        level = models.Level(name="level 2")
        level.save()

        project_list = staff_list['projects']

        staff_list["staff_4"] = models.Staff(project=project_list['project_6'],
                                             employee_type=et_sal,
                                             funding_source=self.cbase_funding,
                                             user=self.regular_user,
                                             level=level,
                                             overtime_hours=1.25,
                                             cost=110.5,
                                             lead=True)
        staff_list["staff_4"].save()

        staff_list["staff_1"].lead = True
        staff_list["staff_1"].save()

        staff_list["staff_2"].lead = True
        staff_list["staff_2"].save()
        return staff_list

    # == The IPSProgramList view requires administrative or management login to use ==

    # if the user isn't logged in they should be directed to the login page
    @tag('ips_program_list', 'access')  # <== I use tags for sorting my unit test, not required
    def test_IPSProgramList_response_login_required_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        response = self.client.get(self.view_url)

        # test that a 302 code is returned. 302 means the user is being redirected
        self.assertEqual(302, response.status_code)

        # We set the browsers active language to 'en' above so we should get the
        # english URL
        self.assertEquals(self.login_url_en, response.url)

    # if the user isn't logged in they should be directed to the login page, en français
    @tag('ips_program_list', 'access')
    def test_IPSProgramList_response_login_required_fr(self):
        # activate is used to set the language of the mock users' browser
        activate('fr')

        response = self.client.get(self.view_url)

        # test that a 302 code is returned. 302 means the user is being redirected
        self.assertEqual(302, response.status_code)

        # We set the browsers active language to 'fr' above so we should get the
        # english URL
        self.assertEquals(self.login_url_fr, response.url)

    # TODO: what should happen if the user is logged in, but isn't a manager or admin
    # if the user logged, and is a manager/admin, in they get a 200 code
    @tag('ips_program_list', 'access')
    def test_IPSProgramList_response_login_regular_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.regular_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        self.fail("I don't know what should happen here. What if the user is logged in, but not an admin or manager")

    # == The IPSProgramList view uses the template projects/ips_program_list.html ==

    # if the user logged, and is a manager/admin, in they get a 200 code
    @tag('ips_program_list', 'access')
    def test_IPSProgramList_response_login_admin_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        self.assertTemplateUsed(response, self.expected_template)

    # IPSProgramList returns a context containing a fiscal year 'fy'
    @tag('ips_program_list', 'context')
    def test_IPSProgramList_response_context_fy_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        self.assertIsNotNone(response.context['fy'])
        self.assertEquals(self.fy, response.context['fy'])

    # IPSProgramList returns a context containing a shared_models.Region 'region'
    @tag('ips_program_list', 'context')
    def test_IPSProgramList_response_context_region_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        self.assertIsNotNone(response.context['region'])
        self.assertEquals(self.region_1, response.context['region'])

    # IPSProgramList returns a context containing dictionary 'my_dict'
    @tag('ips_program_list', 'context')
    def test_IPSProgramList_response_context_my_dict_en(self):
        project_list = self.create_projects()

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        # On to the dictionary testing.
        self.assertIsNotNone(response.context['my_dict'])

        my_dict = response.context['my_dict']

        # = IPSProgramList dictionary 'my_dict' is ordered by division, then section [d][s]
        # = As per the CommonTest.setUp and CommonTest.create_projects.
        # = There are currently 2 divisions belonging to Region 1, with 3 sections between them
        expected_division_count = 2
        expected_section_count = 3

        divisions = my_dict.keys()
        self.assertEquals(expected_division_count, len(divisions))

        section_count = 0
        for d in divisions:
            section_count += len(my_dict[d])

        self.assertEquals(expected_section_count, section_count)

    # == IPSProgramList foreach [d][s] there is a list of projects 'projects' - context['my_dict'][d][s]['projects']
    # === projects for region, for 'fy', submitted=True, section_head_approved=True
    # === distinct division list by section__projects__in=project_list == d
    # === distinct section list by projects__in=project_list == s
    @tag('ips_program_list', 'context')
    def test_IPSProgramList_response_context_my_dict_projects_en(self):
        staff_list = self.create_staff()
        project_list = staff_list['projects']

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        self.assertIsNotNone(response.context['my_dict'])

        my_dict = response.context['my_dict']

        # use the division, section and projects created in this test classes
        # overriding create methods
        projects = my_dict[self.division_112][self.section_1122]['projects']
        self.assertIsNotNone(projects)

        # project 6 was created in TestIPSProgramList.create_projects and should be in
        # section 1122's assigned projects
        self.assertTrue(project_list['project_6'] in projects)

        # in the CommonTest.create_projects method there are 4 projects created for
        # section_1111, but only 2 of those projects are both submitted and approved projects
        s_1111_projects_list = my_dict[self.division_111][self.section_1111]['projects']

        self.assertTrue(project_list['project_4'] in s_1111_projects_list)
        self.assertTrue(project_list['project_1'] in s_1111_projects_list)

        # These are projects created in CommonTest.create_projects, assigned to Section 1111
        # that should not be in the project list because they either were not approved or
        # they were not submitted
        self.assertFalse(project_list['project_2'] in s_1111_projects_list)
        self.assertFalse(project_list['project_3'] in s_1111_projects_list)

    # == IPSProgramList foreach [d][s] there is a list of programs 'programs' - context['my_dict'][d][s]['programs']
    # === for each program p in program_list,
    # ==== project count - context['my_dict'][d][s]['programs'][p]['project_count']
    # ==== leads - context['my_dict'][d][s]['programs'][p]['leads']
    @tag('ips_program_list', 'context')
    def test_IPSProgramList_response_context_my_dict_programs_en(self):
        staff_list = self.create_staff()
        project_list = staff_list['projects']

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        self.assertIsNotNone(response.context['my_dict'])

        my_dict = response.context['my_dict']

        # use the division, section and program created in this test classes
        # overriding create methods
        programs = my_dict[self.division_112][self.section_1122]['programs']
        self.assertIsNotNone(programs)

        # 'programs' is a dictionary where the key is a program
        # check to see if the program we gave a project from
        # this section is in the programs list
        self.assertTrue(self.program2 in programs)

        # == IPSProgramList foreach [d][s]['programs'] there is a list of projects
        # check that that first element in the programs list is assigned to the project
        # given to this section
        program_list = [*programs]
        self.assertTrue(program_list[0] in project_list['project_6'].programs.all())

        # == IPSProgramList foreach [d][s]['program'][p]['project_count'] has the proper project count
        expected_project_count = 1
        program = programs[program_list[0]]
        self.assertEquals(expected_project_count, program['project_count'])

        # test out a program from another division/section that has more than one project
        programs = my_dict[self.division_111][self.section_1111]['programs']
        program_list = [*programs]

        expected_project_count = 2
        program = programs[program_list[0]]
        self.assertEquals(expected_project_count, program['project_count'])

    # == IPSProgramList foreach [d][s]['program'][p]['lead'] has the proper program lead
    # leads are stored as a 'listrify' string, meaning the leads name separated by commas
    @tag('ips_program_list', 'context')
    def test_IPSProgramList_response_context_my_dict_programs_leads_en(self):
        staff_list = self.create_staff()
        project_list = staff_list['projects']

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        my_dict = response.context['my_dict']

        # use the division, section and program created in this test classes
        # overriding create methods
        programs = my_dict[self.division_112][self.section_1122]['programs']

        program_list = [*programs]
        program = programs[program_list[0]]

        expected_project_lead = str(self.regular_user)
        self.assertEquals(expected_project_lead, program['leads'])

        # use the division, section and program created in this test classes
        # overriding create methods
        programs = my_dict[self.division_111][self.section_1111]['programs']

        program_list = [*programs]
        program = programs[program_list[0]]

        # for some reason this doesn't test right. in some cases division_user comes first
        # in other cases regular_user comes first. I'll just check to see if they're in the
        # final string rather than try and recreate the string.
        # TODO: Maybe in the get_context_data
        #  method the users should be sorted alphabetically before the list is created?

        # expected_project_lead = str(self.regular_user) + ", " + str(self.division_user)
        # self.assertEquals(expected_project_lead, program['leads'])

        self.assertTrue(str(self.regular_user) in program['leads'])
        self.assertTrue(str(self.division_user) in program['leads'])


class TestIPSProjectList(CommonTest):

    def setUp(self):
        super().setUp()  # <== Make sure to call the parent class' setUp method
        self.create_org_structure()

        self.fy = shared_models.FiscalYear(full="2019-2020", short="19-20")
        self.fy.save()

        # setup common variables used in tests for this view
        self.view_url = reverse_lazy("projects:ips_project_list",
                                     args=[self.fy.pk, self.section_1111.pk, self.program.pk])
        self.expected_template = 'projects/ips_project_list.html'

        self.expected_url = '/projects/regional-meeting/' + str(self.fy.pk) + \
                            '/section/' + str(self.section_1111.pk) + \
                            '/program/' + str(self.program.pk) + \
                            '/projects/'

        self.expected_url_en = '/en' + self.expected_url
        self.login_url_en = '/accounts/login_required/?next=' + self.expected_url_en

        self.expected_url_fr = '/fr' + self.expected_url
        self.login_url_fr = '/accounts/login_required/?next=' + self.expected_url_fr

    # == The IPSProjectList view requires administrative or management login to use ==

    # if the user isn't logged in they should be directed to the login page
    @tag('ips_project_list', 'access')  # <== I use tags for sorting my unit test, not required
    def test_IPSProjectList_response_login_required_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        response = self.client.get(self.view_url)

        # test that a 302 code is returned. 302 means the user is being redirected
        self.assertEqual(302, response.status_code)

        # We set the browsers active language to 'en' above so we should get the
        # english URL
        self.assertEquals(self.login_url_en, response.url)

    # if the user isn't logged in they should be directed to the login page, en français
    @tag('ips_project_list', 'access')
    def test_IPSProjectList_response_login_required_fr(self):
        # activate is used to set the language of the mock users' browser
        activate('fr')

        response = self.client.get(self.view_url)

        # test that a 302 code is returned. 302 means the user is being redirected
        self.assertEqual(302, response.status_code)

        # We set the browsers active language to 'fr' above so we should get the
        # english URL
        self.assertEquals(self.login_url_fr, response.url)

    # TODO: what should happen if the user is logged in, but isn't a manager or admin
    # if the user logged, and is a manager/admin, in they get a 200 code
    @tag('ips_project_list', 'access')
    def test_IPSProjectList_response_login_regular_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.regular_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        self.fail("I don't know what should happen here. What if the user is logged in, but not an admin or manager")

    # == The IPSProjectList view uses the template projects/ips_project_list.html ==

    # if the user logged, and is a manager/admin, in they get a 200 code
    @tag('ips_project_list', 'access')
    def test_IPSProjectList_response_login_admin_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        self.assertTemplateUsed(response, self.expected_template)

    # The IPSProjectList view returns a fiscal year context object retrieved from the shared_models.FiscalYear table
    # using a passed in ID argument named 'fiscal_year'
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_fy_context_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['fy']
        self.assertIsNotNone(context)
        self.assertEquals(self.fy, context)

    # The IPSProjectList view returns a section context object retrieved from the shared_models.Section table
    # using a passed in ID argument named 'section'
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_section_context_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['section']
        self.assertIsNotNone(context)
        self.assertEquals(self.section_1111, context)

    # The IPSProjectList view returns a program context object retrieved from the projects/models.Program2 table
    # using a passed in ID argument named 'program'
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_program_context_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['program']
        self.assertIsNotNone(context)
        self.assertEquals(self.program, context)

    # The program ID can be null
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_program_null_context_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        tmp_url = reverse_lazy("projects:ips_project_list", args=[self.fy.pk, self.section_1111.pk])
        response = self.client.get(tmp_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['program']
        self.assertIsNone(context)

    # == The IPSProjectList view returns a project_list context object consisting of projects filtered on Section, Year,
    # submitted=True, section_head_approved=True ordered by project id ==

    # What if there are no projects
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_project_list_no_projects_context_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        tmp_url = reverse_lazy("projects:ips_project_list", args=[self.fy.pk, self.section_1111.pk])
        response = self.client.get(tmp_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['project_list']
        self.assertIsNotNone(context)
        self.assertEquals(0, len(context), "The project list should be empty")

    # What if there are projects
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_project_list_some_projects_context_en(self):
        project_list = self.create_projects()

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        tmp_url = reverse_lazy("projects:ips_project_list", args=[self.fy.pk, self.section_1111.pk])
        response = self.client.get(tmp_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['project_list']
        self.assertIsNotNone(context)

        self.assertTrue(project_list['project_1'] in context)

        # Project 2 was not approved, it shouldn't be in the list
        self.assertFalse(project_list['project_2'] in context)

        # Project 3 was a different fiscal year, shouldn't be in the list
        self.assertFalse(project_list['project_3'] in context)

        # Project 5 was a different section, shouldn't be in the list
        self.assertFalse(project_list['project_5'] in context)

        # test the order of the returned list. Project 4 should come before project 1
        self.assertEquals(project_list['project_4'], context[0])
        self.assertEquals(project_list['project_1'], context[1])

    # The IPSProjectList view returns context objects for abase, bbase and cbase containing colours used to colour
    # elements in the HTML. The colours should match values retrieved from the models.FundingSource object
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_funding_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['abase']
        self.assertIsNotNone(context)
        self.assertEquals(self.abase_funding.color, context)

        context = response.context['bbase']
        self.assertIsNotNone(context)
        self.assertEquals(self.bbase_funding.color, context)

        context = response.context['cbase']
        self.assertIsNotNone(context)
        self.assertEquals(self.cbase_funding.color, context)

    # The IPSProjectList view returns context objects of summed salary, om and capital cost for a, b, c, total values
    # retrieved from the project_list
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_a_base_en(self):
        staff_list = self.create_staff()
        project_list = staff_list['projects']

        # the create_projects function only returns 2 projects that should
        # be returned by IPSProjectList. 'project_1' and 'project_4'
        expected_salary = project_list['project_1'].a_salary + project_list['project_4'].a_salary
        expected_om = project_list['project_1'].a_om + project_list['project_4'].a_om
        expected_cap = project_list['project_1'].a_capital + project_list['project_4'].a_capital

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['a_salary']
        self.assertIsNotNone(context)
        self.assertEquals(expected_salary, context)

        context = response.context['a_om']
        self.assertIsNotNone(context)
        self.assertEquals(expected_om, context)

        context = response.context['a_capital']
        self.assertIsNotNone(context)
        self.assertEquals(expected_cap, context)

    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_b_base_en(self):
        staff_list = self.create_staff()
        project_list = staff_list['projects']

        # the create_projects function only returns 2 projects that should
        # be returned by IPSProjectList. 'project_1' and 'project_4'
        expected_salary = project_list['project_1'].b_salary + project_list['project_4'].b_salary
        expected_om = project_list['project_1'].b_om + project_list['project_4'].b_om
        expected_cap = project_list['project_1'].b_capital + project_list['project_4'].b_capital

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['b_salary']
        self.assertIsNotNone(context)
        self.assertEquals(expected_salary, context)

        context = response.context['b_om']
        self.assertIsNotNone(context)
        self.assertEquals(expected_om, context)

        context = response.context['b_capital']
        self.assertIsNotNone(context)
        self.assertEquals(expected_cap, context)

    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_c_base_en(self):
        staff_list = self.create_staff()
        project_list = staff_list['projects']

        # the create_projects function only returns 2 projects that should
        # be returned by IPSProjectList. 'project_1' and 'project_4'
        expected_salary = project_list['project_1'].c_salary + project_list['project_4'].c_salary
        expected_om = project_list['project_1'].c_om + project_list['project_4'].c_om
        expected_cap = project_list['project_1'].c_capital + project_list['project_4'].c_capital

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['c_salary']
        self.assertIsNotNone(context)
        self.assertEquals(expected_salary, context)

        context = response.context['c_om']
        self.assertIsNotNone(context)
        self.assertEquals(expected_om, context)

        context = response.context['c_capital']
        self.assertIsNotNone(context)
        self.assertEquals(expected_cap, context)

    # The IPSProjectList view returns a context objects for total_ot summed from projects in
    # the project_list
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_ot_en(self):
        staff_list = self.create_staff()
        project_list = staff_list['projects']

        # the create_projects function only returns 2 projects that should
        # be returned by IPSProjectList. 'project_1' and 'project_4'
        expected_ot_sum = project_list['project_1'].total_ot + project_list['project_4'].total_ot

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['total_ot']
        self.assertIsNotNone(context)
        self.assertEquals(expected_ot_sum, context)

    # The IPSProjectList view returns a context object total_fte summed from projects in
    # the project_list
    @tag('ips_project_list', 'context')
    def test_IPSProjectList_response_fte_en(self):
        staff_list = self.create_staff()
        project_list = staff_list['projects']

        # the create_projects function only returns 2 projects that should
        # be returned by IPSProjectList. 'project_1' and 'project_4'
        expected_fte_sum = project_list['project_1'].total_fte + project_list['project_4'].total_fte

        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        context = response.context['total_fte']
        self.assertIsNotNone(context)
        self.assertEquals(expected_fte_sum, context)


class TestIPSProjectUpdateView(CommonTest):
    # The IPSProjectUpdateView appears to be an update view that allows updating projects
    # It seems to run on some form of electricity (0_o)

    static_project_list = None

    def setUp(self):
        super().setUp()
        self.create_org_structure()

        self.fy = shared_models.FiscalYear(full="2019-2020", short="19-20")
        self.fy.save()

        self.static_project_list = self.create_projects()

        project = self.static_project_list['project_1']
        program = self.program

        # setup common variables used in tests for this view
        self.view_url_1 = reverse_lazy("projects:ips_project_edit", args=[project.pk])

        self.expected_template = 'projects/ips_project_form.html'

        self.expected_url_base = '/projects/regional-meeting'
        self.expected_url_1 = self.expected_url_base + '/project/' + str(project.pk) + '/'
        self.expected_url_2 = self.expected_url_1 + 'program/' + str(program.pk)

        self.expected_url_en = '/en' + self.expected_url_1
        self.login_url_en = '/accounts/login_required/?next=' + self.expected_url_en

        self.expected_url_fr = '/fr' + self.expected_url_1
        self.login_url_fr = '/accounts/login_required/?next=' + self.expected_url_fr

    # == The IPSProjectUpdateView requires administrative or management login to use ==

    # from the urls.py it looks like this has two URLs to access the view
    # path('regional-meeting/project/<int:pk>/program/<int:program>/', views.IPSProjectUpdateView.as_view(),
    #       name="ips_project_edit"),
    # path('regional-meeting/project/<int:pk>/', views.IPSProjectUpdateView.as_view(), name="ips_project_edit"),

    # if the user isn't logged in they should be directed to the login page
    @tag('ips_project_update_view', 'access')  # <== I use tags for sorting my unit test, not required
    def test_IPSProjectUpdateView_response_login_required_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        response = self.client.get(self.view_url_1)

        # test that a 302 code is returned. 302 means the user is being redirected
        self.assertEqual(302, response.status_code)

        # We set the browsers active language to 'en' above so we should get the
        # english URL
        self.assertEquals(self.login_url_en, response.url)

    # if the user isn't logged in they should be directed to the login page, en français
    @tag('ips_project_update_view', 'access')
    def test_IPSProjectUpdateView_response_login_required_fr(self):
        # activate is used to set the language of the mock users' browser
        activate('fr')

        response = self.client.get(self.view_url_1)

        # test that a 302 code is returned. 302 means the user is being redirected
        self.assertEqual(302, response.status_code)

        # We set the browsers active language to 'fr' above so we should get the
        # english URL
        self.assertEquals(self.login_url_fr, response.url)

    # TODO: what should happen if the user is logged in, but isn't a manager or admin
    # if the user logged, and is a manager/admin, in they get a 200 code
    @tag('ips_project_update_view', 'access')
    def test_IPSProjectUpdateView_response_login_regular_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.regular_user.username, password=self.test_password)

        response = self.client.get(self.view_url_1)

        self.fail("I don't know what should happen here. What if the user is logged in, but not an admin or manager")

    # == The IPSProjectList view uses the template projects/ips_project_list.html ==

    # if the user logged, and is a manager/admin, in they get a 200 code
    @tag('ips_project_update_view', 'access')
    def test_IPSProjectUpdateView_response_login_admin_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(self.view_url_1)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        self.assertTemplateUsed(response, self.expected_template)

    # == IPSProjectUpdateView.form_validation returns an HttpResponseRedirect object

    # If the update view has kwargs["program"] then return a redirect to self.expected_url_2
    # which contains a reference to a program
    @tag('ips_project_update_view', 'form_valid')
    def test_IPSProjectUpdateView_form_valid_w_program_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        project = self.static_project_list['project_1']
        view_url = reverse_lazy("projects:ips_project_edit", args=[project.pk, self.program.pk])

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        data_for_form = {
            'meeting_notes': 'Some notes'
        }

        response = self.client.post(view_url, data_for_form)

        # the user should be redirected. 302 REDIRECT
        self.assertEquals(302, response.status_code)

        expected_url = reverse_lazy('projects:ips_project_list', kwargs={
            "fiscal_year": self.static_project_list['project_1'].year.pk,
            "section": self.static_project_list['project_1'].section.pk,
            "program": self.program.pk
        })
        self.assertEquals(expected_url, response.url)

    # else if the updateview does not have kwargs["program"] redirect to self.expected_url_1, which
    # does not contain a reference to a program
    @tag('ips_project_update_view', 'form_valid')
    def test_IPSProjectUpdateView_form_valid_wo_program_en(self):
        # activate is used to set the language of the mock users' browser
        activate('en')

        project = self.static_project_list['project_1']
        view_url = reverse_lazy("projects:ips_project_edit", args=[project.pk])

        # log the user in
        self.client.login(username=self.admin_user.username, password=self.test_password)

        response = self.client.get(view_url)

        # test that a 200 code is returned. 200 OK
        self.assertEqual(200, response.status_code)

        data_for_form = {
            'meeting_notes': 'Some notes'
        }

        response = self.client.post(view_url, data_for_form)

        # the user should be redirected. 302 REDIRECT
        self.assertEquals(302, response.status_code)

        expected_url = reverse_lazy('projects:ips_project_list', kwargs={
            "fiscal_year": self.static_project_list['project_1'].year.pk,
            "section": self.static_project_list['project_1'].section.pk
        })
        self.assertEquals(expected_url, response.url)
