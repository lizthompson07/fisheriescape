import datetime
import factory
from django.utils import timezone
from faker import Faker

from shared_models.test.SharedModelsFactoryFloor import UserFactory
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


class TransactionCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TransactionCategory

    type = factory.lazy_attribute(lambda o: faker.word())


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Organisation

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
        }


class ExperienceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Experience

    name = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.word(),
        }


class PersonnelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Personnel

    organisation = factory.SubFactory(OrganisationFactory)
    exp_level = factory.SubFactory(ExperienceFactory)
    first_name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'organisation': OrganisationFactory().id,
            'exp_level': ExperienceFactory().id,
            'first_name': faker.catch_phrase(),
        }


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Location

    location = factory.lazy_attribute(lambda o: faker.catch_phrase())
    address = factory.lazy_attribute(lambda o: faker.address())

    @staticmethod
    def get_valid_data():
        return {
            'location': faker.catch_phrase(),
            'address': faker.address(),
        }


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


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Transaction

    item = factory.SubFactory(ItemFactory)
    category = factory.SubFactory(TransactionCategoryFactory)
    location = factory.SubFactory(LocationFactory)
    created_by = factory.SubFactory(UserFactory)
    quantity = factory.lazy_attribute(lambda o: faker.pyint(1, 100))
    created_at = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))
    updated_at = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'item': ItemFactory().id,
            'category': TransactionCategoryFactory().id,
            'location': LocationFactory().id,
            'created_by': UserFactory().id,
            'quantity': faker.pyint(1, 100),
            'created_at': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'updated_at': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
        }


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Order

    item = factory.SubFactory(ItemFactory)
    date_ordered = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'item': ItemFactory().id,
            'date_ordered': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
        }


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Supplier

    supplier_name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'supplier_name': faker.catch_phrase(),
        }


class FileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.File

    item = factory.SubFactory(ItemFactory)
    caption = factory.lazy_attribute(lambda o: faker.catch_phrase())
    file = factory.lazy_attribute(lambda o: faker.catch_phrase())
    date_uploaded = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'item': ItemFactory().id,
            'caption': faker.catch_phrase(),
            'file': faker.catch_phrase(),
            'date_uploaded': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
        }
