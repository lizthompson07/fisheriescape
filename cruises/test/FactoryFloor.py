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

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    instrument_type = factory.lazy_attribute(lambda o: faker.pyint(1, 2))

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
            'instrument_type': faker.pyint(1, 2),
            'is_active': True,
        }


class InstrumentComponentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InstrumentComponent

    instrument = factory.SubFactory(InstrumentFactory)
    component_type = factory.lazy_attribute(
        lambda o: models.ComponentType.objects.all()[faker.random_int(0, models.ComponentType.objects.count() - 1)])
    is_active = factory.lazy_attribute(lambda o: True)

    @staticmethod
    def get_valid_data():
        return {
            'instrument': InstrumentFactory().id,
            'component_type': models.ComponentType.objects.all()[faker.random_int(0, models.ComponentType.objects.count() - 1)].id,
            'is_active': True,
        }
