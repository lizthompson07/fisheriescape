from io import StringIO

import factory
from django.contrib.gis.geos import MultiPolygon, fromstr, Point
from faker import Faker

from .. import models

faker = Faker()


# TODO not sure how to test a multipolygon field for FisheryArea model - create a static polygon
def get_multipolygon():
    # p1 = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
    # p2 = Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))
    p1 = fromstr('POLYGON ((0 0, 0 50, 50 50, 50 0, 0 0))', srid=4326)
    # p1 = Polygon()
    mp = MultiPolygon(p1)
    # mp = MultiPolygon([p1, p2])
    return mp


class FisheryAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FisheryArea

    layer_id = factory.lazy_attribute(lambda o: faker.catch_phrase())
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    polygon = get_multipolygon()

    @staticmethod
    def get_valid_data():
        return {
            'layer_id': faker.catch_phrase(),
            'name': faker.catch_phrase(),
            'polygon': get_multipolygon(),
        }


class NAFOAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NAFOArea

    layer_id = factory.lazy_attribute(lambda o: faker.catch_phrase())
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    polygon = get_multipolygon()

    @staticmethod
    def get_valid_data():
        return {
            'layer_id': faker.catch_phrase(),
            'name': faker.catch_phrase(),
            'polygon': get_multipolygon(),
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


class WeekFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Week

    week_number = factory.lazy_attribute(lambda o: faker.pyint(1, 53))

    @staticmethod
    def get_valid_data():
        return {
            'week_number': faker.pyint(1, 53),
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

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'fishery_areas': [FisheryAreaFactory().id],
        }


class AnalysesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Analyses

    species = factory.SubFactory(SpeciesFactory)
    week = factory.SubFactory(WeekFactory)

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'week': WeekFactory().id,
        }


class MitigationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Mitigation

    mitigation_type = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'mitigation_type': faker.catch_phrase(),
        }


class HexagonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Hexagon

    polygon = get_multipolygon()

    @staticmethod
    def get_valid_data():
        return {
            'polygon': get_multipolygon(),
        }


class ScoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Score

    hexagon = factory.SubFactory(HexagonFactory)
    species = factory.SubFactory(SpeciesFactory)
    week = factory.SubFactory(WeekFactory)
    fs_score = factory.lazy_attribute(lambda o: faker.pydecimal(positive=True, left_digits=4, right_digits=4))

    @staticmethod
    def get_valid_data():
        return {
            'hexagon': HexagonFactory().id,
            'species': SpeciesFactory().id,
            'week': WeekFactory().id,
            'fs_score': faker.pydecimal(positive=True),
        }


class VulnerableSpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.VulnerableSpecies

    english_name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'english_name': faker.catch_phrase(),
        }


class VulnerableSpeciesSpotsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.VulnerableSpeciesSpot

    vulnerable_species = factory.SubFactory(VulnerableSpeciesFactory)
    week = factory.SubFactory(WeekFactory)
    date = faker.date()
    count = factory.lazy_attribute(lambda o: faker.random_int(min=0, max=100))
    point = factory.lazy_attribute(lambda o: Point(faker.latlng()))

    @staticmethod
    def get_valid_data():
        return {
            'point': Point(faker.latlng()),
            'vulnerable_species': VulnerableSpeciesFactory().id,
            'week': WeekFactory().id,
            'count': faker.random_int(min=0, max=100),
        }

