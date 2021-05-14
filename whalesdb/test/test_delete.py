from django.urls import reverse_lazy
from django.test import tag, RequestFactory
from django.contrib import auth, messages
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import activate

from whalesdb.test import WhalesdbFactoryFloor as factory
from whalesdb import models, views
from shared_models.test import common_tests

req_factory = RequestFactory()


class CommonTestFixtures(common_tests.CommonTest):
    fixtures = ['initial_whale_data.json']


@tag("delete", "rsc")
class TestRscDeleteView(CommonTestFixtures):
    view = views.RscDeleteView
    model = models.RscRecordingSchedule

    def setUp(self):
        super().setUp()
        self.instance = factory.RscFactory()
        self.test_url = reverse_lazy('whalesdb:delete_rsc', args=[self.instance.pk, ])
        self.expected_template = 'whalesdb/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="whalesdb_admin")

    @tag("view")
    def test_view_class(self):
        self.assert_inheritance(self.view, views.CommonDeleteView)

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit")
    def test_submit(self):
        data = factory.RscFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("whalesdb:delete_rsc", f"/en/whalesdb/delete/rsc/{self.instance.pk}/", [self.instance.pk])


@tag("delete", "stn")
class TestStnDeleteView(CommonTestFixtures):
    view = views.StnDeleteView
    model = models.StnStation

    def setUp(self):
        super().setUp()
        self.instance = factory.StnFactory()
        self.test_url = reverse_lazy('whalesdb:delete_stn', args=[self.instance.pk, ])
        self.expected_template = 'whalesdb/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="whalesdb_admin")

    @tag("view")
    def test_view_class(self):
        self.assert_inheritance(self.view, views.CommonDeleteView)

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit")
    def test_submit(self):
        data = factory.StnFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("whalesdb:delete_stn", f"/en/whalesdb/delete/stn/{self.instance.pk}/", [self.instance.pk])


@tag("delete", "emm")
class TestEmmDeleteView(CommonTestFixtures):
    view = views.EmmDeleteView
    model = models.EmmMakeModel

    def setUp(self):
        super().setUp()
        self.instance = factory.EmmFactory()
        self.test_url = reverse_lazy('whalesdb:delete_emm', args=[self.instance.pk, ])
        self.expected_template = 'whalesdb/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="whalesdb_admin")

    @tag("view")
    def test_view_class(self):
        self.assert_inheritance(self.view, views.CommonDeleteView)

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit")
    def test_submit(self):
        self.assert_success_url(self.test_url, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("whalesdb:delete_emm", f"/en/whalesdb/delete/emm/{self.instance.pk}/", [self.instance.pk])

    # For the make and model deletion, often the Emm is linked in a one to one relationship with either a
    # hydrophone or a recorder, This causes issues with the standard CommonDeleteView I copied from the SCUBA
    # app so these one-to-one relationships need to be dealt with before the Emm object can be deleted.
    def test_delete_eqr(self):
        emm = factory.EmmFactory(eqt=models.EqtEquipmentTypeCode.objects.get(pk=1))
        eqr = factory.EqrFactory(emm=emm)
        test_url = reverse_lazy('whalesdb:delete_emm', args=[eqr.emm.pk, ])
        self.assert_success_url(test_url, user=self.user)

        # for delete views...
        self.assertEqual(models.EmmMakeModel.objects.filter(pk=eqr.emm.pk).count(), 0)

    def test_delete_eqh(self):
        emm = factory.EmmFactory(eqt=models.EqtEquipmentTypeCode.objects.get(pk=4))
        eqh = factory.EqhFactory(emm=emm)
        test_url = reverse_lazy('whalesdb:delete_emm', args=[eqh.emm.pk, ])
        self.assert_success_url(test_url, user=self.user)

        # for delete views...
        self.assertEqual(models.EmmMakeModel.objects.filter(pk=eqh.emm.pk).count(), 0)


@tag("delete", "eqp")
class TestEqpDeleteView(CommonTestFixtures):
    view = views.EqpDeleteView
    model = models.EqpEquipment

    def setUp(self):
        super().setUp()
        self.instance = factory.EqpFactory()
        self.test_url = reverse_lazy('whalesdb:delete_eqp', args=[self.instance.pk, ])
        self.expected_template = 'whalesdb/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="whalesdb_admin")

    @tag("view")
    def test_view_class(self):
        self.assert_inheritance(self.view, views.CommonDeleteView)

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit")
    def test_submit(self):
        self.assert_success_url(self.test_url, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("whalesdb:delete_eqp", f"/en/whalesdb/delete/eqp/{self.instance.pk}/", [self.instance.pk])


@tag("delete", "dep")
class TestDepDeleteView(CommonTestFixtures):
    view = views.DepDeleteView
    model = models.DepDeployment

    def setUp(self):
        super().setUp()
        self.instance = factory.DepFactory()
        self.test_url = reverse_lazy('whalesdb:delete_dep', args=[self.instance.pk, ])
        self.expected_template = 'whalesdb/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="whalesdb_admin")

    @tag("view")
    def test_view_class(self):
        self.assert_inheritance(self.view, views.CommonDeleteView)

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit")
    def test_submit(self):
        self.assert_success_url(self.test_url, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("whalesdb:delete_dep", f"/en/whalesdb/delete/dep/{self.instance.pk}/", [self.instance.pk])
