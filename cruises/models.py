import os
from django.dispatch import receiver
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lib.functions.custom_functions import listrify
from shared_models import models as shared_models
from shared_models.models import SimpleLookup


class Instrument(models.Model):
    name = models.CharField(unique=True, max_length=255, verbose_name=_("name"))
    notes = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("cruises:instrument_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

    @property
    def component_list(self):
        return listrify([c for c in self.components.all()])


class ComponentType(SimpleLookup):
    pass


class InstrumentComponent(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="components")
    component_type = models.ForeignKey(ComponentType, on_delete=models.DO_NOTHING, verbose_name=_("component type"),
                                       related_name="components")
    model_number = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("model number"))
    serial_number = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("serial number"))
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        my_str = f'{self.component_type}'
        return my_str


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'cruises/{0}/{1}'.format(instance.mission.mission_number, filename)


class File(models.Model):
    caption = models.CharField(max_length=255)
    mission = models.ForeignKey(shared_models.Cruise, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_directory_path)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.caption


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
