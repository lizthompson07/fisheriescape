import factory
import datetime
from faker import Factory
from django.utils import timezone

from django.contrib.auth import models as django_models

from projects import models
from shared_models.test.SharedModelsFactoryFloor import UserFactory, SectionFactory

faker = Factory.create()




class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ActivityType



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
    activity_type = factory.lazy_attribute(lambda o: models.ActivityType.objects.all()[faker.random_int(0, models.ActivityType.objects.count() - 1)])
    start_date = factory.lazy_attribute(lambda o: faker.date_time(tzinfo=timezone.get_current_timezone()))
    end_date = factory.lazy_attribute(lambda o: o.start_date + datetime.timedelta(days=faker.random_int(1, 365)))