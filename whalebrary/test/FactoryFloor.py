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

    name = factory.lazy_attribute(lambda o: faker.name())


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Item

    item_name = factory.lazy_attribute(lambda o: faker.word())
    description = factory.lazy_attribute(lambda o: faker.text())
    category = factory.SubFactory(CategoryFactory)
    owner = factory.SubFactory(OwnerFactory)
    container = factory.lazy_attribute(lambda o: faker.pybool())
    container_space = factory.lazy_attribute(lambda o: faker.pyint(1, 100))
    gear_type = factory.lazy_attribute(lambda o: models.GearType.objects.all()[faker.random_int(0, models.GearType.objects.count() - 1)])


"""

class Experience(models.Model):
    EXPERIENCE_LEVEL_CHOICES = (
        ('None', _("No previous experience")),
        ('Novice', _("1-2 Necropsies")),
        ('Intermediate', _("3-5 Necropsies")),
        ('Advanced', _("More than 5 Necropsies")),
    )
    name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    nom = models.CharField(max_length=250, blank=True, null=True, verbose_name=_(""))
    description_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("English description"))
    description_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French description"))
    experience = models.CharField(max_length=255, choices=EXPERIENCE_LEVEL_CHOICES, default='None', verbose_name=_("Experience level"))
"""

"""

class Personnel(models.Model):
    first_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("First name"))
    last_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Last name"))
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="people", verbose_name=_("Organisation"), null=True, blank=True)
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Email address"))
    phone = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("Phone number"))
    exp_level = models.ForeignKey(Experience, help_text="Novice 1-2 necropsy, Intermediate 3-5, Advanced more than 5", on_delete=models.DO_NOTHING, related_name="xp",
                                                  verbose_name=_("Experience level"))
    training = models.ManyToManyField(Training, verbose_name=_("Training"))
"""

"""
class Organisation(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("English name"))
    abbrev_name = models.CharField(max_length=255, verbose_name=_("English abbreviated name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French name"))
    abbrev_nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("French abbreviated name"))
"""

"""

class Training(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)
"""


# here is my template factory
# class MyModelFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = models.MyModel
#
#     my_word = factory.lazy_attribute(lambda o:faker.word())
#     my_date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))
#     my_float = factory.lazy_attribute(lambda o:faker.pyfloat(positive=True))
#     my_int = factory.lazy_attribute(lambda o:faker.pyint(1,100))
#     my_text = factory.lazy_attribute(lambda o:faker.text())
#     my_bool = factory.lazy_attribute(lambda o:faker.pybool())
#     my_currency = factory.lazy_attribute(lambda o:faker.currency())
#     my_phrase = factory.lazy_attribute(lambda o:faker.catch_phrase())
#     my_company_name = factory.lazy_attribute(lambda o:faker.company())
#     my_phone = factory.lazy_attribute(lambda o:faker.phone_number())
#     my_address = factory.lazy_attribute(lambda o:faker.address())
#     fk_fixture = factory.lazy_attribute(lambda o: models.FK.objects.all()[faker.random_int(0, models.FK.objects.count() - 1)])
#     fk_factory = factory.SubFactory(FK)
