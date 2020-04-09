import factory
import datetime
from faker import Factory
from django.utils import timezone

from django.contrib.auth import models as django_models

from projects import models
from shared_models import models as shared_models

faker = Factory.create()


class FiscalYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = shared_models.FiscalYear


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = shared_models.Region

    name = factory.LazyAttribute(lambda o: faker.word())


class BranchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = shared_models.Branch

    region = factory.SubFactory(RegionFactory)
    name = factory.LazyAttribute(lambda o: faker.word())


class DivisionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = shared_models.Division

    branch = factory.SubFactory(BranchFactory)
    name = factory.LazyAttribute(lambda o: faker.word())


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = shared_models.Section

    division = factory.SubFactory(DivisionFactory)
    name = factory.LazyAttribute(lambda o: faker.word())


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ActivityType


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = django_models.User

    first_name = factory.LazyAttribute(lambda o: faker.name())
    last_name = factory.LazyAttribute(lambda o: faker.name())
    username = factory.LazyAttribute(lambda o: "{}.{}@dfo-mpo.gc.ca".format(o.first_name, o.last_name))


class StaffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Staff

    user = factory.SubFactory(UserFactory)


class IndeterminateStaffFactory(StaffFactory):
    employee_type = models.EmployeeType.objects.get(pk=1)


class StudentStaffFactory(StaffFactory):
    employee_type = models.EmployeeType.objects.get(pk=4)


class OMCostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OMCost

    budget_requested = factory.lazy_attribute(lambda o: faker.random_int(100, 1000))


class OMCostTravelFactory(OMCostFactory):
    om_category = models.OMCategory.objects.get(pk=1)


class OMCostEquipmentFacotry(OMCostFactory):
    om_category = models.OMCategory.objects.get(pk=5)


class ProjectFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Project

    section = factory.SubFactory(SectionFactory)
    activity_type = factory.lazy_attribute(lambda o: models.ActivityType.objects.get(pk=faker.random_int(1, 8)))
    start_date = factory.lazy_attribute(lambda o: faker.date_time(tzinfo=timezone.get_current_timezone()))
    end_date = factory.lazy_attribute(lambda o: o.start_date + datetime.timedelta(days=faker.random_int(1, 365)))