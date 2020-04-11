import factory
from django.contrib.auth.models import User
from faker import Faker
from shared_models import models as shared_models
from django.contrib.auth.hashers import make_password

faker = Faker()
test_password = "test1234"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    first_name = faker.first_name()
    last_name = faker.last_name()
    email = f"{first_name}.{last_name}@dfo-mpo.gc.ca"
    username = email
    password = make_password(test_password)

    @staticmethod
    def get_test_password():
        return test_password

    @staticmethod
    def get_fresh_data():
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = f"{first_name}.{last_name}@dfo-mpo.gc.ca"

        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": email,
            "password": make_password(test_password),
        }


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = shared_models.Section
        django_get_or_create = ('name',)

    name = faker.word()
    head = UserFactory()

    @staticmethod
    def get_fresh_data():
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = f"{first_name}.{last_name}@dfo-mpo.gc.ca"

        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": email,
            "password": "test1234",
        }
