import factory
from django.utils import timezone
from faker import Factory

from .. import models

faker = Factory.create()


class SpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Species

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    scientific_name = factory.lazy_attribute(lambda o: faker.word())
    code = factory.lazy_attribute(lambda o: faker.pyint(1, 10000))
    aphia_id = factory.lazy_attribute(lambda o: faker.pyint(1, 10000))
    is_default = factory.lazy_attribute(lambda o: faker.pybool())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
            'scientific_name': faker.word(),
            'code': faker.pyint(1, 100),
            'aphia_id': faker.pyint(1, 100),
            'is_default': faker.pybool(),
        }


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Region

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    abbreviation = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
            'abbreviation': faker.word(),
        }


class TransectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Transect

    region = factory.SubFactory(RegionFactory)
    name = factory.lazy_attribute(lambda o: faker.pyint(0, 100))

    @staticmethod
    def get_valid_data():
        return {
            'region': RegionFactory().id,
            'name': faker.pyint(0, 100),
        }


class DiverFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Diver

    first_name = factory.lazy_attribute(lambda o: faker.first_name())
    last_name = factory.lazy_attribute(lambda o: faker.last_name())

    @staticmethod
    def get_valid_data():
        return {
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }


class SampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Sample

    transect = factory.SubFactory(TransectFactory)
    datetime = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))
    is_training = factory.lazy_attribute(lambda o: faker.pybool())

    @staticmethod
    def get_valid_data():
        return {
            'transect': TransectFactory().id,
            'datetime': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'is_training': faker.pybool(),
        }


class DiveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Dive

    sample = factory.SubFactory(SampleFactory)
    diver = factory.SubFactory(DiverFactory)
    width_m = factory.lazy_attribute(lambda o: faker.pyint(1, 100))

    @staticmethod
    def get_valid_data(sample):
        return {
            'sample': sample.id,
            'diver': DiverFactory().id,
            'width_m': faker.pyint(1, 100),
            'is_training': False,
        }


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Section

    dive = factory.SubFactory(DiveFactory)
    interval = factory.lazy_attribute(lambda o: faker.pyint(1, 20))
    depth_ft = factory.lazy_attribute(lambda o: faker.pyint(1, 100))

    @staticmethod
    def get_valid_data():
        return {
            'dive': DiveFactory().id,
            'interval': faker.pyint(1, 20),
            'depth_ft': faker.pyint(1, 100),
        }


class ObservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Observation

    section = factory.SubFactory(SectionFactory)
    species = factory.SubFactory(SpeciesFactory)
    sex = factory.lazy_attribute(lambda o: models.Observation.sex_choices[faker.random_int(0, len(models.Observation.sex_choices) - 1)][0])
    certainty_rating = factory.lazy_attribute(lambda o: faker.pyint(0, 1))
    carapace_length_mm = factory.lazy_attribute(lambda o: faker.pyfloat(positive=True))

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'section_id': SectionFactory().id,
            'sex': models.Observation.sex_choices[faker.random_int(0, len(models.Observation.sex_choices) - 1)][0],
            'certainty_rating': faker.pyint(0, 1),
            'carapace_length_mm': faker.pyfloat(positive=True),
        }
