import factory
from faker import Faker

from shared_models.test.SharedModelsFactoryFloor import CruiseFactory
from .. import models

faker = Faker()


class FileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.File

    cruise = factory.SubFactory(CruiseFactory)
    caption = factory.lazy_attribute(lambda o: faker.text())
    file = factory.lazy_attribute(lambda o: faker.url())

    @staticmethod
    def get_valid_data():
        return {
            'cruise': CruiseFactory().id,
            'caption': faker.text(),
        }


class InstrumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Instrument

    cruise = factory.SubFactory(CruiseFactory)
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'cruise': CruiseFactory().id,
            'name': faker.catch_phrase(),
        }


class InstrumentComponentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InstrumentComponent

    instrument = factory.SubFactory(InstrumentFactory)
    component_type = factory.lazy_attribute(
        lambda o: models.ComponentType.objects.all()[faker.random_int(0, models.ComponentType.objects.count() - 1)])

    @staticmethod
    def get_valid_data():
        return {
            'instrument': InstrumentFactory().id,
            'component_type': models.ComponentType.objects.all()[faker.random_int(0, models.ComponentType.objects.count() - 1)].id,
        }
