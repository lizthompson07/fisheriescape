from django.urls import reverse_lazy
from django.test import tag, RequestFactory
from django.contrib import auth, messages
from django.utils.translation import activate

from whalesdb.test import WhalesdbFactoryFloor as factory
from whalesdb import models, views
from shared_models.test import common_tests

req_factory = RequestFactory()


class CommonTestFixtures(common_tests.CommonTest):
    fixtures = ['initial_whale_data.json']


@tag("delete", "rsc")
class TestDeleteRsc(CommonTestFixtures):
    rsc = None

    def setUp(self):
        self.rsc = factory.RscFactory()

        # What if the rsc is attached to a dataset
        factory.RecFactory(rsc_id=self.rsc)

        # What if the rsc is attached to a recording stage
        factory.RstFactory(rsc=self.rsc)

    def test_rsc_delete_not_whale_admin(self):
        self.get_and_login_user()

        activate('en')
        response = self.client.get(reverse_lazy("whalesdb:delete_rsc", args=(self.rsc.pk,)))

        self.assertEqual(1, len(models.RscRecordingSchedule.objects.filter(pk=self.rsc.pk)))

        # redirect to access denied
        self.assertEqual(302, response.status_code)

    def test_rsc_delete_recorder(self):
        self.get_and_login_user(in_group='whalesdb_admin')

        activate('en')
        response = self.client.get(reverse_lazy("whalesdb:delete_rsc", args=(self.rsc.pk,)))

        self.assertEqual(0, len(models.RscRecordingSchedule.objects.filter(pk=self.rsc.pk)))

        # if successful should return a message
        message = str(messages.get_messages(response.wsgi_request)._queued_messages[0])
        self.assertEqual(message, "The Recording Schedule has been successfully deleted.")

        # redirect to HTTP_REFERER
        self.assertEqual(302, response.status_code)


@tag("delete", "stn")
class TestDeleteStn(CommonTestFixtures):
    stn = None

    def setUp(self):
        self.stn = factory.StnFactory()

        # What if a station is used in a deployment
        factory.DepFactory.create(stn=self.stn)

    def test_stn_delete_not_whale_admin(self):
        self.get_and_login_user()

        activate('en')
        response = self.client.get(reverse_lazy("whalesdb:delete_stn", args=(self.stn.pk,)))

        self.assertEqual(1, len(models.StnStation.objects.filter(pk=self.stn.pk)))

        # redirect to access denied
        self.assertEqual(302, response.status_code)

    def test_stn_delete_recorder(self):
        self.get_and_login_user(in_group='whalesdb_admin')

        activate('en')
        response = self.client.get(reverse_lazy("whalesdb:delete_stn", args=(self.stn.pk,)))

        self.assertEqual(0, len(models.StnStation.objects.filter(pk=self.stn.pk)))

        # if successful should return a message
        message = str(messages.get_messages(response.wsgi_request)._queued_messages[0])
        self.assertEqual(message, "The Station has been successfully deleted.")

        # redirect to HTTP_REFERER
        self.assertEqual(302, response.status_code)


@tag("delete", "emm")
class TestDeleteEmm(CommonTestFixtures):
    emm = None

    def setUp(self):
        self.emm = factory.EmmFactory()

        # What if a piece of equipment uses a make/model
        factory.EqpFactory(emm=self.emm)

    def test_emm_delete_not_whale_admin(self):
        self.get_and_login_user()

        activate('en')
        response = self.client.get(reverse_lazy("whalesdb:delete_emm", args=(self.emm.pk,)))

        self.assertEqual(1, len(models.EmmMakeModel.objects.filter(pk=self.emm.pk)))

        #redirect to access denied
        self.assertEqual(302, response.status_code)

    def test_emm_delete_recorder(self):
        self.get_and_login_user(in_group='whalesdb_admin')

        activate('en')
        response = self.client.get(reverse_lazy("whalesdb:delete_emm", args=(self.emm.pk,)))

        self.assertEqual(0, len(models.EmmMakeModel.objects.filter(pk=self.emm.pk)))

        # if successful should return a message
        message = str(messages.get_messages(response.wsgi_request)._queued_messages[0])
        self.assertEqual(message, "The Make/Model has been successfully deleted.")

        # redirect to HTTP_REFERER
        self.assertEqual(302, response.status_code)


@tag("delete", "eqp")
class TestDeleteEqp(CommonTestFixtures):

    eqr = None
    eqh = None

    eqp_rec = None
    eqp_hyd = None

    def setUp(self):
        # create a recorder
        self.eqr = factory.EqrFactory.create()
        # create a hydrophone
        self.eqh = factory.EqhFactory.create()

        # make them equipment
        self.eqp_rec = factory.EqpFactory.create(emm=self.eqr.emm)
        self.eqp_hyd = factory.EqpFactory.create(emm=self.eqh.emm)

        # attach the hydrophone to the recorder
        factory.EheFactory.create(rec=self.eqp_rec, hyd=self.eqp_hyd)

        # attach the recorder to a deployment
        factory.EdaFactory.create(eqp=self.eqp_rec)

        # attach to a Calibration Event
        factory.EcaFactory.create(eca_attachment=self.eqp_rec, eca_hydrophone=self.eqp_hyd)

        # attach to a technical repair event
        factory.EtrFactory.create(eqp=self.eqp_rec, hyd=self.eqp_hyd)

    def test_eqp_delete_recorder(self):
        self.delete_eqp(self.eqp_rec)

    def test_eqp_delete_hydrophone(self):
        self.delete_eqp(self.eqp_hyd)

    def delete_eqp(self, eqp):
        self.get_and_login_user(in_group='whalesdb_admin')

        activate('en')
        response = self.client.get(reverse_lazy("whalesdb:delete_eqp", args=(eqp.pk,)))

        self.assertEqual(0, len(models.EqpEquipment.objects.filter(pk=eqp.pk)))

        # if successful should return a message
        message = str(messages.get_messages(response.wsgi_request)._queued_messages[0])
        self.assertEqual(message, "The equipment has been successfully deleted.")

        # redirect to HTTP_REFERER
        self.assertEqual(302, response.status_code)

    def test_eqp_delete_not_whale_admin(self):
        self.get_and_login_user()

        activate('en')
        response = self.client.get(reverse_lazy("whalesdb:delete_eqp", args=(self.eqp_rec.pk,)))

        self.assertEqual(1, len(models.EqpEquipment.objects.filter(pk=self.eqp_rec.pk)))

        #redirect to access denied
        self.assertEqual(302, response.status_code)