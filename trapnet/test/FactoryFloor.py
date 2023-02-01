import factory
from django.utils import timezone
from faker import Factory

from .. import models

faker = Factory.create()


class BiologicalDetailingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BiologicalDetailing

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.word(),
        }

