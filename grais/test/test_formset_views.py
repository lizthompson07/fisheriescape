from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from shared_models.test.common_tests import CommonTest
from ..test import FactoryFloor
from shared_models.views import CommonFormsetView, CommonHardDeleteView
from ..views import biofouling_views, shared_views
from .. import models, mixins
from faker import Factory

faker = Factory.create()


class TestAllFormsets(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url_names = [
            "manage_probes",
            "manage_samplers",
            "manage_weather_conditions",
        ]

        self.test_urls = [reverse_lazy("grais:" + name) for name in self.test_url_names]
        self.test_views = [
            shared_views.ProbeFormsetView,
            shared_views.SamplerFormsetView,
            shared_views.WeatherConditionFormsetView,
        ]
        self.expected_template = 'grais/formset.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag('formsets', "view")
    def test_view_class(self):
        for v in self.test_views:
            self.assert_inheritance(v, mixins.GraisAdminRequiredMixin)
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
            {"model": models.Probe, "url_name": "delete_probe", "view": shared_views.ProbeHardDeleteView},
            {"model": models.Sampler, "url_name": "delete_sampler", "view": shared_views.SamplerHardDeleteView},
            {"model": models.WeatherConditions, "url_name": "delete_weather_condition", "view": shared_views.WeatherConditionHardDeleteView},
        ]
        self.test_dicts = list()

        self.user = self.get_and_login_user(in_group="grais_admin")
        for d in self.starter_dicts:
            new_d = d
            m = d["model"]
            if m == models.Probe:
                obj = FactoryFloor.ProbeFactory()
            elif m == models.Sampler:
                obj = FactoryFloor.SamplerFactory()
            elif m == models.WeatherConditions:
                obj = FactoryFloor.WeatherConditionsFactory()
            else:
                obj = m.objects.create(name=faker.word())
            new_d["obj"] = obj
            new_d["url"] = reverse_lazy("grais:" + d["url_name"], kwargs={"pk": obj.id})
            self.test_dicts.append(new_d)

    @tag('hard_delete', "view")
    def test_view_class(self):
        for d in self.test_dicts:
            self.assert_inheritance(d["view"], mixins.GraisAdminRequiredMixin)
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
