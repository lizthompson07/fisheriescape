from datetime import timedelta
from decimal import Decimal

from django.test import tag
from datetime import datetime, timedelta
from bio_diversity.test import BioFactoryFloor
from shared_models.test.common_tests import CommonTest
from bio_diversity import models, utils


@tag("Grp", 'models')
class TestGrpModel(CommonTest):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.grp = BioFactoryFloor.GrpFactory()
        self.trof = BioFactoryFloor.TrofFactory(name='1')
        self.trof_two = BioFactoryFloor.TrofFactory(name='2', facic_id=self.trof.facic_id)
        self.evnt_date = utils.naive_to_aware(datetime.today() - timedelta(days=100))
        self.evnt = BioFactoryFloor.EvntFactory(start_datetime=self.evnt_date, facic_id=self.trof.facic_id)
        self.cleaned_data = {
            "facic_id": self.evnt.facic_id,
            "evnt_id": self.evnt,
            "created_by": self.evnt.created_by,
            "created_date": self.evnt.created_date,
        }
        self.contx, data_entered = utils.enter_contx(self.trof, self.cleaned_data, None, return_contx=True)
        self.contx_two, data_entered = utils.enter_contx(self.trof_two, self.cleaned_data, None, return_contx=True)
        temp_envc = models.EnvCode.objects.filter(name="Temperature").get()
        # add ten days worth of temp data to the trough
        for temp in range(0, 10):
            env_date = utils.naive_to_aware(self.evnt.start_date + timedelta(days=temp))
            utils.enter_env(temp, env_date, self.cleaned_data, temp_envc, contx=self.contx)
        for temp in range(10, 20):
            env_date = utils.naive_to_aware(self.evnt.start_date + timedelta(days=temp))
            utils.enter_env(temp, env_date, self.cleaned_data, temp_envc, contx=self.contx_two)

    def test_development(self):
        # test grp placed in trof
        entry_date = self.evnt_date - timedelta(days=1)
        utils.create_movement_evnt(None, self.trof, self.cleaned_data, entry_date, grp_pk=self.grp.pk)
        grp_dev = self.grp.get_development()
        # compare to hard coded value corresponding to 10 days of sequential temperature increases:
        self.assertEqual(round(grp_dev, 3),  round(Decimal(5.579), 3))

    def test_movement_development(self):
        # test grp placed in trof and moved to second trof
        entry_date = self.evnt_date - timedelta(days=1)
        move_date = self.evnt_date + timedelta(days=10)
        utils.create_movement_evnt(None, self.trof, self.cleaned_data, entry_date, grp_pk=self.grp.pk)
        utils.create_movement_evnt(self.trof, self.trof_two, self.cleaned_data, move_date, grp_pk=self.grp.pk)
        grp_dev = self.grp.get_development()
        self.assertEqual(round(grp_dev, 3), round(Decimal(27.854), 3))

    def test_development_after_detail(self):
        # test grp placed in trof, has development recorded go off of that and don't double count
        entry_date = self.evnt_date - timedelta(days=1)
        utils.create_movement_evnt(None, self.trof, self.cleaned_data, entry_date, grp_pk=self.grp.pk)

        det_date = self.evnt_date + timedelta(days=5)
        det_evnt_cleaned_data = utils.create_new_evnt(self.cleaned_data, "Picking", det_date)
        anix = utils.enter_anix(det_evnt_cleaned_data, grp_pk=self.grp.pk, return_anix=True)
        utils.enter_grpd(anix.pk, det_evnt_cleaned_data, det_date, 10,  None, anidc_str="Development")
        grp_dev = self.grp.get_development()
        self.assertEqual(round(grp_dev, 3), round(Decimal(14.015), 3))

    def test_move_and_detail_development(self):
        # test grp placed in trof, get a detail recorded and then moved to second trof
        entry_date = self.evnt_date - timedelta(days=1)
        det_date = self.evnt_date + timedelta(days=5)
        move_date = self.evnt_date + timedelta(days=10)
        det_evnt_cleaned_data = utils.create_new_evnt(self.cleaned_data, "Picking", det_date)
        anix = utils.enter_anix(det_evnt_cleaned_data, grp_pk=self.grp.pk, return_anix=True)
        utils.enter_grpd(anix.pk, det_evnt_cleaned_data, det_date, 10, None, anidc_str="Development")
        utils.create_movement_evnt(None, self.trof, self.cleaned_data, entry_date, grp_pk=self.grp.pk)
        utils.create_movement_evnt(self.trof, self.trof_two, self.cleaned_data, move_date, grp_pk=self.grp.pk)
        grp_dev = self.grp.get_development()
        self.assertEqual(round(grp_dev, 3), round(Decimal(36.291), 3))


@tag("Grpd", 'models')
class TestGrpdModel(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.IndvdFactory.build_valid_data()

    def test_makes_invalid(self):
        # test that previous details with same code are made invalid
        initial_instance = BioFactoryFloor.GrpdFactory(adsc_id=None)
        initial_id = initial_instance.pk
        initial_instance.pk = None
        initial_instance.detail_date = datetime.strptime(initial_instance.detail_date, "%Y-%m-%d") + timedelta(days=1)
        self.assertTrue(models.GroupDet.objects.filter(pk=initial_id).get().grpd_valid)
        initial_instance.save()
        self.assertFalse(models.GroupDet.objects.filter(pk=initial_id).get().grpd_valid)


@tag("Indvd", 'models')
class TestIndvdModel(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.IndvdFactory.build_valid_data()

    def test_makes_invalid(self):
        # test that previous details with same code are made invalid
        initial_instance = BioFactoryFloor.IndvdFactory(adsc_id=None)
        initial_id = initial_instance.pk
        initial_instance.pk = None
        initial_instance.detail_date = datetime.strptime(initial_instance.detail_date, "%Y-%m-%d") + timedelta(days=1)
        self.assertTrue(models.IndividualDet.objects.filter(pk=initial_id).get().indvd_valid)
        initial_instance.save()
        self.assertFalse(models.IndividualDet.objects.filter(pk=initial_id).get().indvd_valid)


@tag("Loc", 'models')
class TestLocModel(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.loc = BioFactoryFloor.LocFactory()
        self.loc.relc_id = None
        models.ReleaseSiteCode.objects.all().delete()
        self.relc = BioFactoryFloor.RelcFactory()
    
    def test_find_relc_from_point(self):
        # test that given no relc_id one is not set based off of location:
        self.loc.loc_lat = self.relc.min_lat
        self.loc.loc_lon = self.relc.min_lon
        self.loc.save()
        self.assertEqual(self.loc.relc_id, None)

    def test_no_relc_no_point(self):
        # test that given no relc_id one is not set based off of location:
        self.loc.loc_lat = None
        self.loc.loc_lon = None
        self.loc.save()
        self.assertEqual(self.loc.relc_id, None)

    def test_find_relc_from_end_point(self):
        # test that given only an endpoint inside the relc, it is not found:
        self.loc.loc_lat = self.relc.min_lat - 1
        self.loc.loc_lon = self.relc.min_lon - 1
        self.loc.end_lat = self.relc.min_lat
        self.loc.end_lon = self.relc.min_lon
        self.loc.save()
        self.assertEqual(self.loc.relc_id, None)

    def test_find_relc_from_line(self):
        # test that with the line intersecting the relc, but with neither point inside, the relc is not found
        self.loc.loc_lat = self.relc.min_lat - 1
        self.loc.loc_lon = self.relc.min_lon - 1
        self.loc.end_lat = self.relc.max_lat + 1
        self.loc.end_lon = self.relc.max_lon + 1
        self.loc.save()
        self.assertEqual(self.loc.relc_id, None)

    def test_point_in_different_relc(self):
        # test that with a relc declared and a point in a different relc, the relc is not replaced
        self.loc.relc_id = self.relc
        new_relc = BioFactoryFloor.RelcFactory()
        self.loc.loc_lat = new_relc.min_lat
        self.loc.loc_lon = new_relc.min_lon
        self.loc.save()
        self.assertEqual(self.loc.relc_id, self.relc)

    def test_point_in_two_relc(self):
        # test that when a point is in two relc it uses neither:
        self.loc.loc_lat = self.relc.min_lat
        self.loc.loc_lon = self.relc.min_lon
        small_relc = self.relc
        small_relc.id = None
        small_relc.name = BioFactoryFloor.RelcFactory.build_valid_data()["name"]
        small_relc.max_lat = self.loc.loc_lat + 0.001
        small_relc.max_lon = self.loc.loc_lon + 0.001
        small_relc.save()
        self.loc.save()
        self.assertEqual(self.loc.relc_id, None)
