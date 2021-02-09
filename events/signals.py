import os

from django.db import models
from django.dispatch import receiver

from .models import Resource


# @receiver(models.signals.post_delete, sender=Resource)
# def auto_delete_file_on_delete(sender, instance, **kwargs):
#     """
#     Deletes file from filesystem
#     when corresponding `MediaFile` object is deleted.
#     """
#     if instance.file_en:
#         if os.path.isfile(instance.file_en.path):
#             os.remove(instance.file_en.path)
#     if instance.file_fr:
#         if os.path.isfile(instance.file_fr.path):
#             os.remove(instance.file_fr.path)
#
#
# @receiver(models.signals.pre_save, sender=Resource)
# def auto_delete_file_on_change(sender, instance, **kwargs):
#     """
#     Deletes old file from filesystem
#     when corresponding `MediaFile` object is updated
#     with new file.
#     """
#     if not instance.pk:
#         return False
#
#     try:
#         old_file = Resource.objects.get(pk=instance.pk).file_en
#     except Resource.DoesNotExist:
#         return False
#
#     new_file = instance.file_en
#     if not old_file == new_file:
#         if os.path.isfile(old_file.path):
#             os.remove(old_file.path)
#
#
#     try:
#         old_file = Resource.objects.get(pk=instance.pk).file_fr
#     except Resource.DoesNotExist:
#         return False
#
#     new_file = instance.file_fr
#     if not old_file == new_file:
#         if os.path.isfile(old_file.path):
#             os.remove(old_file.path)