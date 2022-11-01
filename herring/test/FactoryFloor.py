import factory
from faker import Factory

from shared_models.models import Port
from shared_models.test.SharedModelsFactoryFloor import UserFactory
from .. import models

faker = Factory.create()


class SpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Species

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    aphia_id = factory.lazy_attribute(lambda o: faker.pyint(0, 1000000))
    length_type = factory.lazy_attribute(lambda o: faker.pyint(1, 2))

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
            'aphia_id': faker.pyint(0, 1000000),
            'length_type': faker.pyint(1, 2),
        }


class SamplerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Sampler

    first_name = factory.lazy_attribute(lambda o: faker.word())
    last_name = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'first_name': faker.word(),
            'last_name': faker.word(),
        }


class GearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Gear

    gear = factory.lazy_attribute(lambda o: faker.word())
    gear_code = factory.lazy_attribute(lambda o: faker.pyint(1, 100))

    @staticmethod
    def get_valid_data():
        return {
            'gear': faker.word(),
            'gear_code': faker.pyint(1, 100),
        }


class FishingAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FishingArea

    nafo_area_name = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'nafo_area_name': faker.word(),
        }


class MeshSizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MeshSize

    size_mm = factory.lazy_attribute(lambda o: faker.pyint(1, 100))

    @staticmethod
    def get_valid_data():
        return {
            'size_mm': faker.pyint(1, 100),
        }


class HerringUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.HerringUser

    user = factory.SubFactory(UserFactory)

    @staticmethod
    def get_valid_data():
        return {
            'user': UserFactory().id,
        }


class PortFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Port

    province_code = factory.lazy_attribute(lambda o: str(faker.pyint(1,5)))
    district_code = factory.lazy_attribute(lambda o: str(faker.pyint(10,99)))
    port_code = factory.lazy_attribute(lambda o: str(faker.pyint(10,99)))
    port_name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'province_code': str(faker.pyint(1,5)),
            'district_code': str(faker.pyint(10,99)),
            'port_code': str(faker.pyint(10,99)),
            'port_name': faker.word(),
        }
