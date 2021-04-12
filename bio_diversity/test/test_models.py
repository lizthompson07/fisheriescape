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

        self.assertTrue(False)


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


