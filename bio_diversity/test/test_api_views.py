from django.test import tag
from django.urls import reverse
from django.utils import timezone
from faker import Factory
from rest_framework import status

from . import BioFactoryFloor
from .. import models
from shared_models.test.common_tests import CommonTest

faker = Factory.create()


@tag("api", 'current-user')
class TestCurrentUser(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.test_url = reverse("bio-current-user")

    def test_url(self):
        self.assert_correct_url("bio-current-user", expected_url_path=f"/api/bio_diversity/user/")

    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data(self):
        data = self.client.get(self.test_url).data
        keys = ["id", "first_name", "last_name", "username", "is_admin"]
        self.assert_dict_has_keys(data, keys)

    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


@tag("api", 'api-indv')
class TestIndividual(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = BioFactoryFloor.IndvFactory()
        self.test_url = "{}?pit_tag={}".format(reverse("api-indv"), self.instance.pit_tag)

    def test_url(self):
        self.assert_correct_url("api-indv", expected_url_path=f"/api/bio_diversity/indv/")

    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data(self):
        data = self.client.get(self.test_url).data[0]
        keys = ["id", "ufid", "pit_tag", "coll_id", "spec_id"]
        self.assert_dict_has_keys(data, keys)

    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


@tag("api", 'api-anix')
class TestAnix(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = BioFactoryFloor.AnixFactory()
        self.test_url = "{}?id={}".format(reverse("api-anix"), self.instance.pk)

    def test_url(self):
        self.assert_correct_url("api-anix", expected_url_path=f"/api/bio_diversity/anix/")

    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data(self):
        data = self.client.get(self.test_url).data[0]
        keys = ["id", "evnt_id", "loc_id", "indv_id", "pair_id", "grp_id"]
        self.assert_dict_has_keys(data, keys)

    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


@tag("api", 'api-cup')
class TestCup(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = BioFactoryFloor.CupFactory()
        self.test_url = "{}?id={}".format(reverse("api-cup"), self.instance.pk)

    def test_url(self):
        self.assert_correct_url("api-cup", expected_url_path=f"/api/bio_diversity/cup/")

    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data(self):
        data = self.client.get(self.test_url).data[0]
        keys = ["id", "name", "nom", "description_en", "description_fr", "drawer", "draw_id", "heath_unit",
                "start_date", "end_date"]
        self.assert_dict_has_keys(data, keys)

    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


@tag("api", 'api-contx')
class TestContx(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = BioFactoryFloor.ContxFactory()
        self.test_url = "{}?id={}".format(reverse("api-contx"), self.instance.pk)

    def test_url(self):
        self.assert_correct_url("api-contx", expected_url_path=f"/api/bio_diversity/contx/")

    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data(self):
        data = self.client.get(self.test_url).data[0]
        keys = ["id", "evnt_id", "cup_id", "draw_id", "heat_id", "tank_id", "tray_id", "trof_id"]
        self.assert_dict_has_keys(data, keys)

    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


@tag("api", 'api-cnt')
class TestCnt(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = BioFactoryFloor.CntFactory()
        self.test_url = "{}?id={}".format(reverse("api-cnt"), self.instance.pk)

    def test_url(self):
        self.assert_correct_url("api-cnt", expected_url_path=f"/api/bio_diversity/cnt/")

    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data(self):
        data = self.client.get(self.test_url).data[0]
        keys = ["id", "count_code", "loc_id", "cntc_id", "spec_id", "cnt", "est", "comments", ]
        self.assert_dict_has_keys(data, keys)

    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)


@tag("api", 'api-grp')
class TestGrp(CommonTest):
    def setUp(self):
        super().setUp()
        self.user = self.get_and_login_user()
        self.instance = BioFactoryFloor.GrpFactory()
        self.test_url = "{}?id={}".format(reverse("api-grp"), self.instance.pk)

    def test_url(self):
        self.assert_correct_url("api-grp", expected_url_path=f"/api/bio_diversity/grp/")

    def test_authenticated(self):
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_response_data(self):
        data = self.client.get(self.test_url).data[0]
        keys = ["id","spec_id", "stok_id", "coll_id", "grp_year", "grp_valid", "comments", "species", "stock",
                "collection" ]
        self.assert_dict_has_keys(data, keys)

    def test_safe_methods_only(self):
        restricted_statuses = [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        self.assertIn(self.client.put(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.delete(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.post(self.test_url, data=None).status_code, restricted_statuses)
        self.assertIn(self.client.patch(self.test_url, data=None).status_code, restricted_statuses)

