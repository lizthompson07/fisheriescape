from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from faker import Factory

from shared_models.views import CommonFormsetView, CommonHardDeleteView
from .common_tests import CommonHerringTest as CommonTest
from .. import models
from .. import views
from ..test import FactoryFloor

faker = Factory.create()


class TestHerringUserFormsets(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url_names = [
            "manage_herring_users",
        ]

        self.test_urls = [reverse_lazy("herring:" + name) for name in self.test_url_names]
        self.test_views = [
            views.HerringUserFormsetView,
        ]
        self.expected_template = 'herring/formset.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag('formsets', "view")
    def test_view_class(self):
        for v in self.test_views:
            self.assert_inheritance(v, views.SuperuserOrAdminRequiredMixin)
            self.assert_inheritance(v, CommonFormsetView)

    @tag('formsets', "access")
    def test_view(self):
        for url in self.test_urls:
            self.assert_good_response(url)
            self.assert_non_public_view(test_url=url, expected_template=self.expected_template, user=self.user)

    @tag('formsets', "submit")
    def test_submit(self):
        data = dict()  # should be fine to submit with empty data
        for url in self.test_urls:
            self.assert_success_url(url, data=data)



class TestHerringUserHardDeleteViews(CommonTest):
    def setUp(self):
        super().setUp()
        self.starter_dicts = [
            {"model": models.HerringUser, "url_name": "delete_herring_user", "view": views.HerringUserHardDeleteView},
        ]
        self.test_dicts = list()

        self.user = self.get_and_login_user(is_admin=True)
        for d in self.starter_dicts:
            new_d = d
            m = d["model"]
            obj = FactoryFloor.HerringUserFactory()
            new_d["obj"] = obj
            new_d["url"] = reverse_lazy("herring:" + d["url_name"], kwargs={"pk": obj.id})
            self.test_dicts.append(new_d)

    @tag('hard_delete', "view")
    def test_view_class(self):
        for d in self.test_dicts:
            self.assert_inheritance(d["view"], views.SuperuserOrAdminRequiredMixin)
            self.assert_inheritance(d["view"], CommonHardDeleteView)

    @tag('hard_delete', "access")
    def test_view(self):
        for d in self.test_dicts:
            self.assert_good_response(d["url"])
            # only have one chance to test this url
            self.assert_non_public_view(test_url=d["url"], user=self.user, expected_code=302, locales=["en"])

    @tag('hard_delete', "delete")
    def test_delete(self):
        # need to be an admin user to do this
        self.get_and_login_user(user=self.user)
        for d in self.test_dicts:
            # start off to confirm the object exists
            self.assertIn(d["obj"], type(d["obj"]).objects.all())
            # visit the url
            activate("en")
            self.client.get(d["url"])
            # confirm the object has been deleted
            self.assertNotIn(d["obj"], type(d["obj"]).objects.all())



class TestAllFormsets(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url_names = [
            "manage_samplers",
            "manage_gears",
            "manage_fishing_areas",
            "manage_mesh_sizes",
        ]

        self.test_urls = [reverse_lazy("herring:" + name) for name in self.test_url_names]
        self.test_views = [
            views.SamplerFormsetView,
            views.GearFormsetView,
            views.FishingAreaFormsetView,
            views.MeshSizeFormsetView,
        ]
        self.expected_template = 'herring/formset.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag('formsets', "view")
    def test_view_class(self):
        for v in self.test_views:
            self.assert_inheritance(v, views.HerringAdmin)
            self.assert_inheritance(v, CommonFormsetView)

    @tag('formsets', "access")
    def test_view(self):
        for url in self.test_urls:
            self.assert_good_response(url)
            self.assert_non_public_view(test_url=url, expected_template=self.expected_template, user=self.user)

    @tag('formsets', "submit")
    def test_submit(self):
        data = dict()  # should be fine to submit with empty data
        for url in self.test_urls:
            self.assert_success_url(url, data=data)


class TestAllHardDeleteViews(CommonTest):
    def setUp(self):
        super().setUp()
        self.starter_dicts = [
            {"model": models.Sampler, "url_name": "delete_sampler", "view": views.SamplerHardDeleteView},
            {"model": models.Gear, "url_name": "delete_gear", "view": views.GearHardDeleteView},
            {"model": models.FishingArea, "url_name": "delete_fishing_area", "view": views.FishingAreaHardDeleteView},
            {"model": models.MeshSize, "url_name": "delete_mesh_size", "view": views.MeshSizeHardDeleteView},
        ]
        self.test_dicts = list()

        self.user = self.get_and_login_user(is_admin=True)
        for d in self.starter_dicts:
            new_d = d
            m = d["model"]
            if m == models.Sampler:
                obj = FactoryFloor.SamplerFactory()
            elif m == models.Gear:
                obj = FactoryFloor.GearFactory()
            elif m == models.FishingArea:
                obj = FactoryFloor.FishingAreaFactory()
            elif m == models.MeshSize:
                obj = FactoryFloor.MeshSizeFactory()
            else:
                obj = m.objects.create(name=faker.word())
            new_d["obj"] = obj
            new_d["url"] = reverse_lazy("herring:" + d["url_name"], kwargs={"pk": obj.id})
            self.test_dicts.append(new_d)

    @tag('hard_delete', "view")
    def test_view_class(self):
        for d in self.test_dicts:
            self.assert_inheritance(d["view"], views.HerringAdmin)
            self.assert_inheritance(d["view"], CommonHardDeleteView)

    @tag('hard_delete', "access")
    def test_view(self):
        for d in self.test_dicts:
            self.assert_good_response(d["url"])
            # only have one chance to test this url
            self.assert_non_public_view(test_url=d["url"], user=self.user, expected_code=302, locales=["en"])

    @tag('hard_delete', "delete")
    def test_delete(self):
        # need to be an admin user to do this
        self.get_and_login_user(user=self.user)
        for d in self.test_dicts:
            # start off to confirm the object exists
            self.assertIn(d["obj"], type(d["obj"]).objects.all())
            # visit the url
            activate("en")
            self.client.get(d["url"])
            # confirm the object has been deleted
            self.assertNotIn(d["obj"], type(d["obj"]).objects.all())
