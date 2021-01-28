import factory
from django.utils import timezone
from faker import Factory

from .. import models

faker = Factory.create()


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


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Site

    region = factory.SubFactory(RegionFactory)
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    abbreviation = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'region': RegionFactory().id,
            'name': faker.catch_phrase(),
            'abbreviation': faker.word(),
        }


class TransectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Transect

    site = factory.SubFactory(SiteFactory)
    name = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'site': SiteFactory().id,
            'name': faker.word(),
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

    site = factory.SubFactory(SiteFactory)
    datetime = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'site': SiteFactory().id,
            'datetime': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
        }


class DiveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Dive

    sample = factory.SubFactory(SampleFactory)
    transect = factory.SubFactory(TransectFactory)
    diver = factory.SubFactory(DiverFactory)
    width_m = factory.lazy_attribute(lambda o: faker.pyint(1, 100))

    @staticmethod
    def get_valid_data(sample):
        site = sample.site
        transect = TransectFactory(site=site)
        return {
            'sample': sample.id,
            'transect': transect.id,
            'diver': DiverFactory().id,
            'width_m': faker.pyint(1, 100),
        }

    @staticmethod
    def get_invalid_data():
        return {
            'sample': SampleFactory().id,
            'transect': TransectFactory().id,
            'diver': DiverFactory().id,
            'width_m': faker.pyint(1, 100),
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
    sex = factory.lazy_attribute(lambda o: models.Observation.sex_choices[faker.random_int(0, len(models.Observation.sex_choices) - 1)][0])
    certainty_rating = factory.lazy_attribute(lambda o: faker.pyint(0, 1))
    carapace_length_mm = factory.lazy_attribute(lambda o: faker.pyfloat(positive=True))

    @staticmethod
    def get_valid_data():
        return {
            'section_id': SectionFactory().id,
            'sex': models.Observation.sex_choices[faker.random_int(0, len(models.Observation.sex_choices) - 1)][0],
            'certainty_rating': faker.pyint(0, 1),
            'carapace_length_mm': faker.pyfloat(positive=True),
        }

