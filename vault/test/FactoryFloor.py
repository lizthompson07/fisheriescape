import datetime
import factory
from django.utils import timezone
from faker import Faker

from shared_models.test.SharedModelsFactoryFloor import UserFactory
from .. import models

faker = Faker()


class SpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Species

    english_name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'english_name': faker.catch_phrase(),
        }


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Role

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
        }


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Organisation

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    abbrev_name = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
            'abbrev_name': faker.word(),
        }


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Person

    organisation = factory.SubFactory(OrganisationFactory)
    first_name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'organisation': OrganisationFactory().id,
            'roles': RoleFactory().id,
            'first_name': faker.catch_phrase(),
        }


class InstrumentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InstrumentType

    mode = factory.lazy_attribute(lambda o: faker.catch_phrase())
    type = factory.lazy_attribute(lambda o: faker.catch_phrase())
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'mode': faker.catch_phrase(),
            'type': faker.catch_phrase(),
            'name': faker.catch_phrase(),
        }


class InstrumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Instrument

    instrument_type = factory.SubFactory(InstrumentTypeFactory)
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'instrument_type': InstrumentTypeFactory().id,
            'name': faker.catch_phrase(),
        }


class ObservationPlatformTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ObservationPlatformType

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
        }


class ObservationPlatformFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ObservationPlatform

    observation_platform_type = factory.SubFactory(ObservationPlatformTypeFactory)
    authority = factory.SubFactory(OrganisationFactory)
    owner = factory.SubFactory(OrganisationFactory)
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'observation_platform_type': ObservationPlatformTypeFactory().id,
            'authority': OrganisationFactory().id,
            'owner': OrganisationFactory().id,
            'name': faker.catch_phrase(),
        }


class OutingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Outing

    observation_platform = factory.SubFactory(ObservationPlatformFactory)
    identifier_string = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'observation_platform': ObservationPlatformFactory().id,
            'identifier_string': faker.catch_phrase(),
        }