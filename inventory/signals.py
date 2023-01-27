import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DMAReview, File, Person, Review


@receiver(models.signals.post_save, sender=DMAReview)
def save_dma_on_review_save(sender, instance, created, **kwargs):
    instance.dma.save()


@receiver(models.signals.post_delete, sender=DMAReview)
def save_dma_on_review_delete(sender, instance, **kwargs):
    instance.dma.save()


@receiver(models.signals.post_save, sender=Review)
def save_resource_on_review_save(sender, instance, created, **kwargs):
    instance.resource.save()


@receiver(models.signals.post_delete, sender=Review)
def save_resource_on_review_delete(sender, instance, **kwargs):
    instance.resource.save()


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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance)
