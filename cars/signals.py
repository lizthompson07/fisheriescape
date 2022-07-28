import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Vehicle, ReferenceMaterial


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
    if old_file.name and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)




@receiver(post_delete, sender=ReferenceMaterial)
def auto_delete_cars_Reference_Material_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file_en:
        if os.path.isfile(instance.file_en.path):
            os.remove(instance.file_en.path)

    if instance.file_fr:
        if os.path.isfile(instance.file_fr.path):
            os.remove(instance.file_fr.path)


@receiver(pre_save, sender=ReferenceMaterial)
def auto_delete_cars_Reference_Material_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file_en = ReferenceMaterial.objects.get(pk=instance.pk).file_en
    except ReferenceMaterial.DoesNotExist:
        return False

    new_file_en = instance.file_en
    if old_file_en and old_file_en != new_file_en:
        if os.path.isfile(old_file_en.path):
            os.remove(old_file_en.path)

    try:
        old_file_fr = ReferenceMaterial.objects.get(pk=instance.pk).file_en
    except ReferenceMaterial.DoesNotExist:
        return False

    new_file_fr = instance.file_en
    if old_file_fr and old_file_fr != new_file_fr:
        if os.path.isfile(old_file_fr.path):
            os.remove(old_file_fr.path)
