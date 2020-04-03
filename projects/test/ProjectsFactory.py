import factory
from faker import Factory

from projects import models
from shared_models import models as shared_models

faker = Factory.create()


class FiscalYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = shared_models.FiscalYear


class ProjectFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Project

    year = factory.SubFactory(FiscalYearFactory)