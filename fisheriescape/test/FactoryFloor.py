import factory
from faker import Faker

from .. import models

faker = Faker()


#TODO not sure how to test a multipolygon field for FisheryArea model

class FisheryAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FisheryArea

    layer_id = factory.lazy_attribute(lambda o: faker.catch_phrase())
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'layer_id': faker.catch_phrase(),
            'name': faker.catch_phrase(),
        }


class SpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Species

    english_name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'english_name': faker.catch_phrase(),
        }


class MarineMammalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MarineMammal

    english_name_short = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'english_name_short': faker.catch_phrase(),
        }


class FisheryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Fishery

    species = factory.SubFactory(SpeciesFactory)
    fishery_area = factory.SubFactory(FisheryAreaFactory)
    marine_mammals = factory.SubFactory(MarineMammalFactory)

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'fishery_area': FisheryAreaFactory().id,
            'marine_mammals': MarineMammalFactory().id,
        }