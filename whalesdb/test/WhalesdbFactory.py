import factory
from faker import Factory

from whalesdb import models
from shared_models import models as shared_models

_stn_codes_ = ['ABC', 'DEF', 'GHI', 'JKL', 'MNO', 'PQR', 'STU', 'VWX', 'YZZ']
_set_codes_ = ['Deployment', 'Recovery']
faker = Factory.create()


class EqpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EqpEquipment

    @staticmethod
    def get_valid_data():
        return {}


class MorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MorMooringSetup
        django_get_or_create = ('mor_name',)

    mor_name = faker.name()
    mor_max_depth = faker.random_int(0, 1000)
    mor_link_setup_image = faker.url()
    mor_additional_equipment = faker.sentence()
    mor_general_moor_description = faker.text()
    mor_notes = faker.text()

    @staticmethod
    def get_valid_data():
        valid_data = {
            "mor_name": faker.name(),
            "mor_max_depth": faker.random_int(0, 1000),

            "mor_link_setup_image": faker.url(),
            "mor_additional_equipment": faker.sentence(),
            "mor_general_moor_description": faker.text(),
            "mor_notes": faker.text()
        }

        return valid_data


class PrjFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PrjProject
        django_get_or_create = ('prj_name',)

    prj_name = faker.name()
    prj_description = faker.text()
    prj_url = faker.url()

    @staticmethod
    def get_valid_data():
        valid_data = {
            "prj_name": faker.name(),
            "prj_description": faker.text(),
            "prj_url": faker.url()
        }

        return valid_data


class StnFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.StnStation
        django_get_or_create = ('stn_code',)

    stn_name = faker.name()
    stn_code = factory.Iterator(_stn_codes_)
    stn_revision = 1
    stn_planned_lat = faker.pydecimal(left_digits=2, right_digits=5)
    stn_planned_lon = faker.pydecimal(left_digits=2, right_digits=5)
    stn_planned_depth = faker.random_int(0, 1000)
    stn_notes = faker.text()

    @staticmethod
    def get_valid_data():
        valid_data = {
            "stn_name": faker.name(),
            "stn_code": factory.Iterator(_stn_codes_),
            "stn_revision": 1,
            "stn_planned_lat": faker.pydecimal(left_digits=2, right_digits=5),
            "stn_planned_lon": faker.pydecimal(left_digits=2, right_digits=5),
            "stn_planned_depth": faker.random_int(0, 1000),
            "stn_notes": faker.text()
        }

        return valid_data


class DepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DepDeployment

    stn = StnFactory.create()
    prj = PrjFactory.create()
    mor = MorFactory.create()
    dep_year = faker.random_int(1980, 2060)
    dep_month = faker.random_int(1, 12)
    dep_name = "{}-{}-{}".format(stn.stn_code, dep_year, dep_month)

    @staticmethod
    def get_valid_data():
        stn = StnFactory.create()
        prj = PrjFactory.create()
        mor = MorFactory.create()
        year = faker.random_int(1980, 2060)
        month = faker.random_int(1, 12)

        valid_data = {
            'stn': stn.pk,
            'dep_year': year,
            'dep_month': month,
            'dep_name': "{}-{}-{}".format(stn.stn_code, year, month),
            'prj': prj.pk,
            'mor': mor.pk,
        }

        return valid_data


class SetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SetStationEventCode
        django_get_or_create = ('set_name',)

    set_name = factory.Iterator(_set_codes_)

# class InstituteFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = shared_models.Institute
#
#
# class VesselFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = shared_models.Vessel


class CruiseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = shared_models.Cruise


class SteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SteStationEvent

    dep = DepFactory.create()
    set_type = SetFactory.create()
    crs = CruiseFactory.create()
    ste_date = faker.date()

    @staticmethod
    def get_valid_data():
        dep = DepFactory()
        set_type = SetFactory.create()
        crs = CruiseFactory.create()

        valid_data = {
            "dep": dep,
            "set_type": set_type,
            "crs": crs,
            "ste_date": faker.date()
        }

        return valid_data
