import datetime
import factory
from django.utils import timezone
from faker import Faker

from shared_models.test.SharedModelsFactoryFloor import SectionFactory, UserFactory
from .. import models

faker = Faker()


class GearTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GearType

    name = factory.lazy_attribute(lambda o: faker.word())


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category

    name = factory.lazy_attribute(lambda o: faker.word())


class OwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Owner
    
    name = factory.lazy_attribute(lambda o: faker.word())


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Item

    owner = factory.SubFactory(OwnerFactory)
    gear_type = factory.SubFactory(GearTypeFactory)
    category = factory.SubFactory(CategoryFactory)
    item_name = factory.lazy_attribute(lambda o: faker.catch_phrase())



    @staticmethod
    def get_valid_data():
        return {
            'owner': OwnerFactory().id,
            'gear_type': GearTypeFactory().id,
            'category': CategoryFactory().id,
            'item_name': faker.catch_phrase(),
        }