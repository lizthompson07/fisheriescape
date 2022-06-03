from django.contrib.auth.models import User
from django.db import models
# Create your models here.
from django.utils.translation import gettext_lazy as _

from shared_models.models import SimpleLookup, Region, MetadataFields, UnilingualSimpleLookup, LatLongFields

YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]


class CarsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cars_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="cars_users", on_delete=models.CASCADE, blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False, verbose_name=_("app administrator?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class VehicleType(SimpleLookup):
    pass


class Location(SimpleLookup, LatLongFields):
    address = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("address"))
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("city"))
    postal_code = models.CharField(max_length=7, blank=True, null=True, verbose_name=_("postal code"))


def img_file_name(instance, filename):
    img_name = 'cars/{}_{}'.format(instance.id, filename)
    return img_name


class Vehicle(MetadataFields):
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    custodian = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="vehicles")
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.DO_NOTHING)
    reference_number = models.CharField(max_length=50, verbose_name=_("reference number"))
    make = models.CharField(max_length=255, verbose_name=_("make"))
    model = models.CharField(max_length=255, verbose_name=_("model"))
    year = models.PositiveIntegerField(verbose_name=_("year"))
    max_passengers = models.PositiveIntegerField(verbose_name=_("max passengers"))
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))
    comments = models.TextField(verbose_name=_("comments"), blank=True, null=True)
    thumbnail = models.ImageField(blank=True, null=True, upload_to=img_file_name, verbose_name=_("thumbnail"))


class Reservation(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("vehicle"), related_name="reservations")
    start_date = models.DateTimeField(verbose_name=_("departure date"))
    end_date = models.DateTimeField(verbose_name=_("return date"))
    primary_driver = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("primary driver"), related_name="reservations")
    other_drivers = models.ManyToManyField(User, blank=True, verbose_name=_("other drivers"))
