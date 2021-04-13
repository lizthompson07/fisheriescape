from datetime import timedelta
from django.test import tag
from datetime import datetime
from bio_diversity.test import BioFactoryFloor
from shared_models.test.common_tests import CommonTest
from bio_diversity import models


@tag("Grp", 'models')
class TestGrpModel(CommonTest):
    fixtures = ["valid_test_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.GrpFactory.build_valid_data()

    def test_development(self):
        # test that previous details with same code are made invalid
        grp = models.Group.objects.filter(pk=46).get()
        grp_dev = grp.get_development()
        self.assertEqual(round(grp_dev, 3),  7.261)


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
        # test that given no relc_id one is set based off of location:
        self.loc.loc_lat = self.relc.min_lat
        self.loc.loc_lon = self.relc.min_lon
        self.loc.save()
        self.assertEqual(self.loc.relc_id, self.relc)

    def test_no_relc_no_point(self):
        # test that given no relc_id one is not set based off of location:
        self.loc.loc_lat = None
        self.loc.loc_lon = None
        self.loc.save()
        self.assertEqual(self.loc.relc_id, None)

    def test_find_relc_from_end_point(self):
        # test that given only an endpoint inside the relc, it is still found:
        self.loc.loc_lat = self.relc.min_lat - 1
        self.loc.loc_lon = self.relc.min_lon - 1
        self.loc.end_lat = self.relc.min_lat
        self.loc.end_lon = self.relc.min_lon
        self.loc.save()
        self.assertEqual(self.loc.relc_id, self.relc)

    def test_find_relc_from_line(self):
        # test that with the line intersecting the relc, but with neither point inside, the relc is still found
        self.loc.loc_lat = self.relc.min_lat - 1
        self.loc.loc_lon = self.relc.min_lon - 1
        self.loc.end_lat = self.relc.max_lat + 1
        self.loc.end_lon = self.relc.max_lon + 1
        self.loc.save()
        self.assertEqual(self.loc.relc_id, self.relc)

    def test_point_in_different_relc(self):
        # test that with a relc declared and a point in a different relc, the relc is not replaced
        self.loc.relc_id = self.relc
        new_relc = BioFactoryFloor.RelcFactory()
        self.loc.loc_lat = new_relc.min_lat
        self.loc.loc_lon = new_relc.min_lon
        self.loc.save()
        self.assertEqual(self.loc.relc_id, self.relc)
