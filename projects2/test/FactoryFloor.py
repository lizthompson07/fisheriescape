import datetime

import factory
from django.utils import timezone
from faker import Factory

from shared_models.test.SharedModelsFactoryFloor import SectionFactory, UserFactory, RegionFactory
from .. import models

faker = Factory.create()


class ThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Theme

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
        }


class FunctionalGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FunctionalGroup

    theme = factory.SubFactory(ThemeFactory)
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'theme': ThemeFactory().id,
            'name': faker.catch_phrase(),
        }


class FundingSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FundingSource

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    funding_source_type = factory.lazy_attribute(lambda o: faker.pyint(1, 3))

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
            'funding_source_type': faker.pyint(1, 2),
        }


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Tag

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
        }


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Project

    section = factory.SubFactory(SectionFactory)
    functional_group = factory.SubFactory(FunctionalGroupFactory)
    default_funding_source = factory.SubFactory(FundingSourceFactory)
    title = factory.lazy_attribute(lambda o: faker.catch_phrase())
    activity_type = factory.lazy_attribute(lambda o: models.ActivityType.objects.all()[faker.random_int(0, models.ActivityType.objects.count() - 1)])

    @staticmethod
    def get_valid_data():
        return {
            'section': SectionFactory().id,
            'functional_group': FunctionalGroupFactory().id,
            'default_funding_source': FundingSourceFactory().id,
            'title': faker.catch_phrase(),
            'activity_type': models.ActivityType.objects.all()[faker.random_int(0, models.ActivityType.objects.count() - 1)].id,
        }


class ProjectYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProjectYear

    project = factory.SubFactory(ProjectFactory)
    status = factory.lazy_attribute(lambda o: faker.pyint(1, 100))
    start_date = factory.lazy_attribute(lambda o: datetime.datetime(year=faker.pyint(2000, 2030), month=4, day=1, tzinfo=timezone.get_current_timezone()))
    end_date = factory.lazy_attribute(lambda o: datetime.datetime(year=o.start_date.year + 1, month=3, day=31, tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        start_date = datetime.datetime(year=faker.pyint(2000, 2030), month=4, day=1, tzinfo=timezone.get_current_timezone())
        end_date = datetime.datetime(year=start_date.year + 1, month=3, day=31, tzinfo=timezone.get_current_timezone())
        return {
            'project': ProjectFactory().id,
            'status': faker.pyint(1, 100),
            'start_date': start_date,
            'end_date': end_date,
        }


class StaffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Staff

    project_year = factory.SubFactory(ProjectYearFactory)
    funding_source = factory.SubFactory(FundingSourceFactory)
    amount = factory.lazy_attribute(lambda o: faker.pyfloat(positive=True))
    is_lead = factory.lazy_attribute(lambda o: faker.pybool())
    user = factory.SubFactory(UserFactory)
    employee_type = factory.lazy_attribute(lambda o: models.EmployeeType.objects.all()[faker.random_int(0, models.EmployeeType.objects.count() - 1)])

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
            'funding_source': FundingSourceFactory().id,
            'amount': faker.pyfloat(positive=True),
            'user': UserFactory().id,
            'is_lead': faker.pybool(),
            'employee_type': models.EmployeeType.objects.all()[faker.random_int(0, models.EmployeeType.objects.count() - 1)].id,
        }


class LeadStaffFactory(StaffFactory):
    is_lead = True


class IndeterminateStaffFactory(StaffFactory):
    employee_type = models.EmployeeType.objects.get(pk=1)


class StudentStaffFactory(StaffFactory):
    employee_type = models.EmployeeType.objects.get(pk=4)


class OMCostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OMCost

    project_year = factory.SubFactory(ProjectYearFactory)
    funding_source = factory.SubFactory(FundingSourceFactory)
    amount = factory.lazy_attribute(lambda o: faker.pyfloat(positive=True))
    om_category = factory.lazy_attribute(lambda o: models.OMCategory.objects.all()[faker.random_int(0, models.OMCategory.objects.count() - 1)])
    description = factory.lazy_attribute(lambda o: faker.text())

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
            'funding_source': FundingSourceFactory().id,
            'amount': faker.pyfloat(positive=True),
            'description': faker.text(),
            'om_category': models.OMCategory.objects.all()[faker.random_int(0, models.OMCategory.objects.count() - 1)].id,
        }


class OMCostTravelFactory(OMCostFactory):
    om_category = models.OMCategory.objects.get(pk=1)


class OMCostEquipmentFactory(OMCostFactory):
    om_category = models.OMCategory.objects.get(pk=5)


class CapitalCostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CapitalCost

    project_year = factory.SubFactory(ProjectYearFactory)
    funding_source = factory.SubFactory(FundingSourceFactory)
    amount = factory.lazy_attribute(lambda o: faker.pyfloat(positive=True))
    category = factory.lazy_attribute(lambda o: faker.pyint(1, 4))

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
            'funding_source': FundingSourceFactory().id,
            'amount': faker.pyfloat(positive=True),
            'category': faker.pyint(1, 4),
        }


class GCCostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GCCost

    project_year = factory.SubFactory(ProjectYearFactory)
    recipient_org = factory.lazy_attribute(lambda o: faker.company())
    amount = factory.lazy_attribute(lambda o: faker.pyfloat(positive=True))

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
            'recipient_org': faker.company(),
            'amount': faker.pyfloat(positive=True),
        }


class CollaboratorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Collaborator

    project_year = factory.SubFactory(ProjectYearFactory)
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    critical = factory.lazy_attribute(lambda o: faker.pybool())

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
            'name': faker.catch_phrase(),
            'critical': faker.pybool(),
        }


class CollaborativeAgreementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CollaborativeAgreement

    project_year = factory.SubFactory(ProjectYearFactory)
    partner_organization = factory.lazy_attribute(lambda o: faker.company())
    new_or_existing = factory.lazy_attribute(lambda o: faker.pyint(1, 2))

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
            'partner_organization': faker.company(),
            'new_or_existing': faker.pyint(1, 2),
        }


class FileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.File

    project = factory.SubFactory(ProjectFactory)
    project_year = factory.SubFactory(ProjectYearFactory)
    name = factory.lazy_attribute(lambda o: faker.text())

    @staticmethod
    def get_valid_data():
        return {
            'project': ProjectFactory().id,
            'project_year': ProjectYearFactory().id,
            'name': faker.text(),
        }


class StatusReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StatusReport

    project_year = factory.SubFactory(ProjectYearFactory)
    status = factory.lazy_attribute(lambda o: faker.pyint(3, 6))

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
            'status': faker.pyint(3, 6),
        }

    @staticmethod
    def get_valid_review_data():
        return {
            'section_head_comments': faker.text(),
            'section_head_reviewed': faker.pybool(),
        }


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Review

    project_year = factory.SubFactory(ProjectYearFactory)

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
        }


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Activity

    project_year = factory.SubFactory(ProjectYearFactory)
    type = factory.lazy_attribute(lambda o: faker.pyint(1, 2))
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())
    target_date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'project_year': ProjectYearFactory().id,
            'type': faker.pyint(1, 2),
            'name': faker.catch_phrase(),
            'target_date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()).strftime("%Y-%m-%d"),
        }


class ActivityUpdateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ActivityUpdate

    activity = factory.SubFactory(ActivityFactory)
    status_report = factory.SubFactory(StatusReportFactory)
    status = factory.lazy_attribute(lambda o: faker.pyint(7, 9))

    @staticmethod
    def get_valid_data():
        return {
            'activity': ActivityFactory().id,
            'status_report': StatusReportFactory().id,
            'status': faker.pyint(1, 100),
        }


class UpcomingDateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UpcomingDate

    region = factory.SubFactory(RegionFactory)
    description_en = factory.lazy_attribute(lambda o: faker.text())
    date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'region': RegionFactory().id,
            'description_en': faker.text(),
            'date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
        }


class ReferenceMaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ReferenceMaterial

    region = factory.SubFactory(RegionFactory)
    file_en = factory.lazy_attribute(lambda o: faker.url())
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'region': RegionFactory().id,
            'file_en': faker.url(),
            'name': faker.catch_phrase(),

        }
