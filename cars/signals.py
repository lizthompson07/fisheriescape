import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Vehicle


@receiver(post_delete, sender=Vehicle)
def auto_delete_thumbnail_on_delete(sender, instance, **kwargs):
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)


@receiver(pre_save, sender=Vehicle)
def auto_delete_thumbnail_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Vehicle.objects.get(pk=instance.pk).thumbnail
    except Vehicle.DoesNotExist:
        return False

    new_file = instance.thumbnail
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
