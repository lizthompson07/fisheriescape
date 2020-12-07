from django.test import tag
from django.urls import reverse
from django.utils import timezone
from faker import Factory
from rest_framework import status

from . import FactoryFloor
from ..test.common_tests import CommonProjectTest as CommonTest

faker = Factory.create()


class TestCurrentUser(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.test_url = reverse("current-user")

    @tag("api", 'current-user')
    def test_url(self):
        self.assert_correct_url("current-user", expected_url_path=f"/api/project-planning/user/")

    @tag("api", 'current-user')
    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @tag("api", 'current-user')
    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'current-user')
    def test_response_data(self):
        data = self.client.get(self.test_url).data
        keys = ["id", "first_name", "last_name", "username", "is_admin", "is_management", "is_rds"]
        self.assert_dict_has_keys(data, keys)

        # check query params
        object = FactoryFloor.ProjectFactory()
        data = self.client.get(self.test_url + f"?project={object.id}").data
        keys.extend(["reason", "can_modify"])
        self.assert_dict_has_keys(data, keys)

        object = FactoryFloor.StatusReportFactory()
        data = self.client.get(self.test_url + f"?status_report={object.id}").data
        keys.extend(["is_section_head"])
        self.assert_dict_has_keys(data, keys)

    @tag("api", 'current-user')
    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestFTEBreakdownAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.test_url = reverse("fte-breakdown", args=None)

    @tag("api", 'fte-breakdown')
    def test_url(self):
        self.assert_correct_url("fte-breakdown", test_url_args=None, expected_url_path=f"/api/project-planning/fte-breakdown/")

    @tag("api", 'fte-breakdown')
    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @tag("api", 'fte-breakdown')
    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'fte-breakdown')
    def test_response_data(self):
        staff1 = FactoryFloor.StaffFactory(user=self.user)
        staff2 = FactoryFloor.StaffFactory(user=self.user)

        data = self.client.get(self.test_url).data

        # Since there was no fiscal year specified, it will be a list of dicts
        keys = [
            'name',
            'fiscal_year',
            'draft',
            'submitted_unapproved',
            'approved',
        ]
        for item in data:
            self.assert_dict_has_keys(item, keys)

        # if we specify a fiscal year, it should just be one obj
        data = self.client.get(self.test_url + f"?year={staff1.project_year.fiscal_year_id}").data
        self.assert_dict_has_keys(data, keys)
        self.assertEqual(data["name"], f"{self.user.last_name}, {self.user.first_name}")

        # we have the option to specify a user
        staff3 = FactoryFloor.StaffFactory(user=self.get_and_login_user())
        data = self.client.get(self.test_url + f"?year={staff3.project_year.fiscal_year_id}").data
        self.assertEqual(data["name"], f"{staff3.user.last_name}, {staff3.user.first_name}")

        # and finally, we should be able to supply a list of project_year ids
        project_year_1 = FactoryFloor.ProjectYearFactory(start_date=timezone.now())
        project_year_2 = FactoryFloor.ProjectYearFactory(start_date=timezone.now())
        staff3 = FactoryFloor.StaffFactory(project_year=project_year_1)
        staff4 = FactoryFloor.StaffFactory(project_year=project_year_2)
        response = self.client.get(self.test_url + f"?ids={project_year_1.id},{project_year_2.id}")
        # but this should return a bad response since no fiscal year was supplied
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(self.test_url + f"?ids={project_year_1.id},{project_year_2.id};year={project_year_2.fiscal_year_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the data should be a list for each user
        data = response.data
        self.assertEqual(len(data), 2)
        keys.append("staff_instances")
        for item in data:
            self.assert_dict_has_keys(item, keys)

    @tag("api", 'fte-breakdown')
    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestProjectRetrieveAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse("project-detail", args=[self.instance.pk])

    @tag("api", 'project-detail')
    def test_url(self):
        self.assert_correct_url("project-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/project-planning/projects/{self.instance.pk}/")

    @tag("api", 'project-detail')
    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @tag("api", 'project-detail')
    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'project-detail')
    def test_response_data(self):
        data = None
        data = self.client.get(self.test_url, data=data).data
        keys = [
            "id",
        ]
        self.assert_dict_has_keys(data, keys)

    @tag("api", 'project-detail')
    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestProjectListAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = FactoryFloor.ProjectFactory()
        self.test_url = reverse("project-list", args=None)

    @tag("api", 'project-list')
    def test_url(self):
        self.assert_correct_url("project-list", test_url_args=None, expected_url_path=f"/api/project-planning/projects/")

    @tag("api", 'project-list')
    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @tag("api", 'project-list')
    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'project-list')
    def test_response_data(self):
        data = self.client.get(self.test_url).data
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.instance.id)

    @tag("api", 'project-list')
    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestProjectYearListAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse("year-list", args=None)

    @tag("api", 'year-list')
    def test_url(self):
        self.assert_correct_url("year-list", test_url_args=None, expected_url_path=f"/api/project-planning/project-years/")

    @tag("api", 'year-list')
    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @tag("api", 'year-list')
    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'year-list')
    def test_response_data(self):
        self.instance.status = 1
        self.instance.save()
        py = FactoryFloor.ProjectYearFactory(status=4, submitted=timezone.now())
        data = self.client.get(self.test_url).data
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], py.id)
        # but if we are an admin user, we should see 2 projects
        self.get_and_login_user(in_group="projects_admin")
        data = self.client.get(self.test_url).data
        self.assertEqual(len(data["results"]), 2)

    @tag("api", 'year-list')
    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestProjectYearRetrieveAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse("year-detail", args=[self.instance.pk])

    @tag("api", 'year-detail')
    def test_url(self):
        self.assert_correct_url("year-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/project-planning/project-years/{self.instance.pk}/")

    @tag("api", 'year-detail')
    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @tag("api", 'year-detail')
    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'year-detail')
    def test_response_data(self):
        data = None
        data = self.client.get(self.test_url, data=data).data
        keys = [
            "id",
        ]
        self.assert_dict_has_keys(data, keys)

    @tag("api", 'year-detail')
    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


class TestProjectYearSubmitAPIView(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = FactoryFloor.ProjectYearFactory()
        self.test_url = reverse("year-submit", args=[self.instance.pk])

    @tag("api", 'year-submit')
    def test_url(self):
        self.assert_correct_url("year-submit", test_url_args=[self.instance.pk],
                                expected_url_path=f"/api/project-planning/project-years/{self.instance.pk}/submit/")

    @tag("api", 'year-submit')
    def test_permissions(self):
        # authenticated users
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # unauthenticated users
        self.client.logout()
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # project lead should be allowed - but will not test extensively the CanModify permissions class since this is done in utils
        staff = FactoryFloor.LeadStaffFactory(project_year=self.instance)
        self.get_and_login_user(user=staff.user)
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    # @tag("api", 'year-submit')
    # def test_response_data(self):
    #     data = None
    #     data = self.client.get(self.test_url, data=data).data
    #     keys = [
    #         "id",
    #     ]
    #     self.assert_dict_has_keys(data, keys)



    @tag("api", 'year-submit')
    def test_unallowed_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.get(self.test_url, data=None).status_code, restricted_statuses)
