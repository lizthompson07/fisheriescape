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


@tag("delete", "dep")
class TestDepDeleteView(CommonTestFixtures):
    view = views.DepDeleteView
    model = models.DepDeployment
    factory = factory.DepFactory
    signature = 'whalesdb:delete_dep'
    url = '/en/whalesdb/delete/dep/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
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
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])


@tag("delete", "eca")
class TestEcaDeleteView(CommonTestFixtures):
    view = views.EcaDeleteView
    model = models.EcaCalibrationEvent
    factory = factory.EcaFactory
    signature = 'whalesdb:delete_eca'
    url = '/en/whalesdb/delete/eca/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk])
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
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])


@tag("delete", "ecc")
class TestEccDeleteView(CommonTestFixtures):
    view = views.EccDeleteView
    model = models.EccCalibrationValue
    factory = factory.EccFactory
    signature = 'whalesdb:delete_ecc'
    url = '/en/whalesdb/delete/ecc/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, 'pop',])
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
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/pop/", [self.instance.pk, 'pop',])


@tag("delete", "ecp")
class TestEcpDeleteView(CommonTestFixtures):
    view = views.EcpDeleteView
    model = models.EcpChannelProperty
    factory = factory.EcpFactory
    signature = 'whalesdb:delete_ecp'
    url = '/en/whalesdb/delete/ecp/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, 'pop'])
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
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/pop/", [self.instance.pk, 'pop'])


@tag("delete", "eda")
class TestEdaDeleteView(CommonTestFixtures):
    view = views.EdaDeleteView
    model = models.EdaEquipmentAttachment
    factory = factory.EdaFactory
    signature = 'whalesdb:delete_eda'
    url = '/en/whalesdb/delete/eda/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, 'pop'])
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
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/pop/", [self.instance.pk, 'pop'])


@tag("delete", "emm")
class TestEmmDeleteView(CommonTestFixtures):
    view = views.EmmDeleteView
    model = models.EmmMakeModel
    factory = factory.EmmFactory
    signature = 'whalesdb:delete_emm'
    url = '/en/whalesdb/delete/emm/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
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
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])

    # For the make and model deletion, often the Emm is linked in a one to one relationship with either a
    # hydrophone or a recorder, This causes issues with the standard CommonDeleteView I copied from the SCUBA
    # app so these one-to-one relationships need to be dealt with before the Emm object can be deleted.
    def test_delete_eqr(self):
        emm = factory.EmmFactory(eqt=models.EqtEquipmentTypeCode.objects.get(pk=1))
        eqr = factory.EqrFactory(emm=emm)
        test_url = reverse_lazy(self.signature, args=[eqr.emm.pk, ])
        self.assert_success_url(test_url, user=self.user)

        # for delete views...
        self.assertEqual(models.EmmMakeModel.objects.filter(pk=eqr.emm.pk).count(), 0)

    def test_delete_eqh(self):
        emm = factory.EmmFactory(eqt=models.EqtEquipmentTypeCode.objects.get(pk=4))
        eqh = factory.EqhFactory(emm=emm)
        test_url = reverse_lazy(self.signature, args=[eqh.emm.pk, ])
        self.assert_success_url(test_url, user=self.user)

        # for delete views...
        self.assertEqual(models.EmmMakeModel.objects.filter(pk=eqh.emm.pk).count(), 0)


@tag("delete", "eqp")
class TestEqpDeleteView(CommonTestFixtures):
    view = views.EqpDeleteView
    model = models.EqpEquipment
    factory = factory.EqpFactory
    signature = 'whalesdb:delete_eqp'
    url = '/en/whalesdb/delete/eqp/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
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
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])


@tag("delete", "mor")
class TestMorDeleteView(CommonTestFixtures):
    view = views.MorDeleteView
    model = models.MorMooringSetup
    factory = factory.MorFactory
    signature = 'whalesdb:delete_mor'
    url = '/en/whalesdb/delete/mor/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
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
        data = factory.MorFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])


@tag("delete", "etr")
class TestEtrDeleteView(CommonTestFixtures):
    view = views.EtrDeleteView
    model = models.EtrTechnicalRepairEvent
    factory = factory.EtrFactory
    signature = 'whalesdb:delete_etr'
    url = '/en/whalesdb/delete/etr/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk])
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
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])


@tag("delete", "prj")
class TestMorDeleteView(CommonTestFixtures):
    view = views.PrjDeleteView
    model = models.PrjProject
    factory = factory.PrjFactory
    signature = 'whalesdb:delete_prj'
    url = '/en/whalesdb/delete/prj/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
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
        data = factory.MorFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])


@tag("delete", "rec")
class TestRecDeleteView(CommonTestFixtures):
    view = views.RecDeleteView
    model = models.RecDataset
    factory = factory.RecFactory
    signature = 'whalesdb:delete_rec'
    url = '/en/whalesdb/delete/rec/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
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
        data = self.factory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])

    @tag("correct_url", "pop")
    def test_correct_pop_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/pop/", [self.instance.pk, "pop"])


@tag("delete", "rci")
class TestRciDeleteView(CommonTestFixtures):
    view = views.RciDeleteView
    model = models.RciChannelInfo
    factory = factory.RciFactory
    signature = 'whalesdb:delete_rci'
    url = '/en/whalesdb/delete/rci/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, 'pop', ])
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
        data = factory.MorFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/pop/", [self.instance.pk, 'pop',])


@tag("delete", "ree")
class TestReeDeleteView(CommonTestFixtures):
    view = views.ReeDeleteView
    model = models.ReeRecordingEvent
    factory = factory.ReeFactory
    signature = 'whalesdb:delete_ree'
    url = '/en/whalesdb/delete/ree/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, 'pop', ])
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
        data = self.factory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/pop/", [self.instance.pk, 'pop', ])


@tag("delete", "rsc")
class TestRscDeleteView(CommonTestFixtures):
    view = views.RscDeleteView
    model = models.RscRecordingSchedule
    factory = factory.RscFactory
    signature = 'whalesdb:delete_rsc'
    url = '/en/whalesdb/delete/rsc/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
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
        data = self.factory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])


@tag("delete", "rst")
class TestRstDeleteView(CommonTestFixtures):
    view = views.RstDeleteView
    model = models.RstRecordingStage
    factory = factory.RstFactory
    signature = 'whalesdb:delete_rst'
    url = '/en/whalesdb/delete/rst/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, 'pop', ])
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
        data = factory.MorFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/pop/", [self.instance.pk, 'pop',])


@tag("delete", "stn")
class TestStnDeleteView(CommonTestFixtures):
    view = views.StnDeleteView
    model = models.StnStation
    factory = factory.StnFactory
    signature = 'whalesdb:delete_stn'
    url = '/en/whalesdb/delete/stn/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
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
        data = self.factory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk])


@tag("delete", "ste")
class TestSteDeleteView(CommonTestFixtures):
    view = views.SteDeleteView
    model = models.SteStationEvent
    factory = factory.SteFactory
    signature = 'whalesdb:delete_ste'
    url = '/en/whalesdb/delete/ste/'

    def setUp(self):
        super().setUp()
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, "pop",])
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
        data = self.factory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/pop/", [self.instance.pk, "pop",])


# The models.TeaTeamMember object is not *required* by anything that uses it so it's ok to delete
# without confirmation
@tag("delete", "tea")
class TestDeleteTea(CommonTestFixtures):

    model = models.TeaTeamMember
    factory = factory.TeaFactory
    signature = 'whalesdb:delete_tea'
    url = '/en/whalesdb/delete/tea/'

    def setUp(self):
        self.instance = self.factory.create()
        self.test_url = reverse_lazy(self.signature, args=[self.instance.pk, ])
        self.user = self.get_and_login_user(in_group="whalesdb_admin")

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, locales=('en',), user=self.user, expected_code=302)

    @tag("submit")
    def test_submit(self):
        self.assert_success_url(self.test_url, user=self.user)

        # for delete views...
        self.assertEqual(self.model.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url(self.signature, f"{self.url}{self.instance.pk}/", [self.instance.pk, ])
