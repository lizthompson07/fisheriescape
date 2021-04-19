import json

from django.test import tag
from django.urls import reverse
from faker import Faker
from rest_framework import status

from shared_models.test.common_tests import CommonTest
from . import FactoryFloor

faker = Faker()


class TestSampleSpeciesAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.crud_user = self.get_and_login_user(in_group="grais_crud")
        self.sample = FactoryFloor.SampleFactory()
        self.instance = FactoryFloor.SampleSpeciesFactory()
        self.test_list_url = reverse("samplespecies-list", args=None) + f"?sample={self.sample.id}"
        self.test_detail_url = reverse("samplespecies-detail", args=[self.instance.pk])

    @tag("api", 'samplespecies')
    def test_url(self):
        self.assert_correct_url("samplespecies-list", test_url_args=None, expected_url_path=f"/api/grais/sample-species/")
        self.assert_correct_url("samplespecies-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/grais/sample-species/{self.instance.pk}/")

    @tag("api", 'samplespecies')
    def test_get(self):
        # authenticated users
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'samplespecies')
    def test_post(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.SampleSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.SampleSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'samplespecies')
    def test_put_patch(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.SampleSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.SampleSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'samplespecies')
    def test_delete(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # unauthenticated users
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLineSpeciesAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.crud_user = self.get_and_login_user(in_group="grais_crud")
        self.line = FactoryFloor.LineFactory()
        self.instance = FactoryFloor.LineSpeciesFactory()
        self.test_list_url = reverse("linespecies-list", args=None) + f"?line={self.line.id}"
        self.test_detail_url = reverse("linespecies-detail", args=[self.instance.pk])

    @tag("api", 'linespecies')
    def test_url(self):
        self.assert_correct_url("linespecies-list", test_url_args=None, expected_url_path=f"/api/grais/line-species/")
        self.assert_correct_url("linespecies-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/grais/line-species/{self.instance.pk}/")

    @tag("api", 'linespecies')
    def test_get(self):
        # authenticated users
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'linespecies')
    def test_post(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.LineSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.LineSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'linespecies')
    def test_put_patch(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.LineSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.LineSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'linespecies')
    def test_delete(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # unauthenticated users
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestSurfaceSpeciesAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.crud_user = self.get_and_login_user(in_group="grais_crud")
        self.surface = FactoryFloor.SurfaceFactory()
        self.instance = FactoryFloor.SurfaceSpeciesFactory()
        self.test_list_url = reverse("surfacespecies-list", args=None) + f"?surface={self.surface.id}"
        self.test_detail_url = reverse("surfacespecies-detail", args=[self.instance.pk])

    @tag("api", 'surfacespecies')
    def test_url(self):
        self.assert_correct_url("surfacespecies-list", test_url_args=None, expected_url_path=f"/api/grais/surface-species/")
        self.assert_correct_url("surfacespecies-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/grais/surface-species/{self.instance.pk}/")

    @tag("api", 'surfacespecies')
    def test_get(self):
        # authenticated users
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'surfacespecies')
    def test_post(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.SurfaceSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.SurfaceSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'surfacespecies')
    def test_put_patch(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.SurfaceSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.SurfaceSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'surfacespecies')
    def test_delete(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # unauthenticated users
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestIncidentalReportSpeciesAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.crud_user = self.get_and_login_user(in_group="grais_crud")
        self.incidentalreport = FactoryFloor.IncidentalReportFactory()
        self.instance = FactoryFloor.IncidentalReportSpeciesFactory()
        self.test_list_url = reverse("incidentalreportspecies-list", args=None) + f"?report={self.incidentalreport.id}"
        self.test_detail_url = reverse("incidentalreportspecies-detail", args=[self.instance.pk])

    @tag("api", 'incidentalreportspecies')
    def test_url(self):
        self.assert_correct_url("incidentalreportspecies-list", test_url_args=None, expected_url_path=f"/api/grais/incidental-report-species/")
        self.assert_correct_url("incidentalreportspecies-detail", test_url_args=[self.instance.pk],
                                expected_url_path=f"/api/grais/incidental-report-species/{self.instance.pk}/")

    @tag("api", 'incidentalreportspecies')
    def test_get(self):
        # authenticated users
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'incidentalreportspecies')
    def test_post(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.IncidentalReportSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.IncidentalReportSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'incidentalreportspecies')
    def test_put_patch(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.IncidentalReportSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.IncidentalReportSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'incidentalreportspecies')
    def test_delete(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # unauthenticated users
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCatchSpeciesAPIViewSet(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.crud_user = self.get_and_login_user(in_group="grais_crud")
        self.trap = FactoryFloor.TrapFactory()
        self.instance = FactoryFloor.CatchSpeciesFactory()
        self.test_list_url1 = reverse("catch-list", args=None) + f"?trap={self.trap.id}&crab=true"
        self.test_list_url2 = reverse("catch-list", args=None) + f"?trap={self.trap.id}&bycatch=true"
        self.test_detail_url1 = reverse("catch-detail", args=[self.instance.pk]) + f"?crab=true"
        self.test_detail_url2 = reverse("catch-detail", args=[self.instance.pk]) + f"?bycatch=true"

    @tag("api", 'catchspecies')
    def test_url(self):
        self.assert_correct_url("catch-list", test_url_args=None, expected_url_path=f"/api/grais/catch-species/")
        self.assert_correct_url("catch-detail", test_url_args=[self.instance.pk], expected_url_path=f"/api/grais/catch-species/{self.instance.pk}/")

    @tag("api", 'catchspecies')
    def test_get(self):
        # authenticated users
        response = self.client.get(self.test_detail_url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.test_detail_url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.test_list_url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.test_list_url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unauthenticated users
        self.client.logout()
        response = self.client.get(self.test_detail_url1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_detail_url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.test_list_url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'catchspecies')
    def test_post(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.CatchSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url1, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.test_list_url2, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.CatchSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response = self.client.post(self.test_list_url1, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(self.test_list_url2, data=data_json, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'catchspecies')
    def test_put_patch(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        data_dict = FactoryFloor.CatchSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url1, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url1, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        response1 = self.client.put(self.test_detail_url2, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url2, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # unauthenticated users
        self.get_and_login_user()
        data_dict = FactoryFloor.CatchSpeciesFactory.get_valid_data()
        data_json = json.dumps(data_dict)
        response1 = self.client.put(self.test_detail_url1, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url1, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        response1 = self.client.put(self.test_detail_url2, data=data_json, content_type="application/json")
        response2 = self.client.patch(self.test_detail_url2, data=data_json, content_type="application/json")
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'catchspecies')
    def test_delete1(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        response = self.client.delete(self.test_detail_url1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # unauthenticated users
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("api", 'catchspecies')
    def test_delete2(self):
        # authenticated users
        self.get_and_login_user(user=self.crud_user)
        response = self.client.delete(self.test_detail_url2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # unauthenticated users
        self.get_and_login_user()
        response = self.client.delete(self.test_detail_url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
