import os

from django.db import models
from django.dispatch import receiver

from .models import ReferenceMaterial, File, Staff, ProjectYear, Review, Project


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

    try:
        new_file = instance.file
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except ValueError:
        return False


@receiver(models.signals.post_delete, sender=ReferenceMaterial)
def auto_delete_ReferenceMaterial_on_delete(sender, instance, **kwargs):
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


@receiver(models.signals.pre_save, sender=ReferenceMaterial)
def auto_delete_ReferenceMaterial_on_change(sender, instance, **kwargs):
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


# @receiver(models.signals.post_delete, sender=Staff)
# def save_project_on_staff_delete(sender, instance, **kwargs):
#     print(instance)
#
#     try:
#         instance.project_year.project.save()
#     except:
#         pass

@receiver(models.signals.post_save, sender=Staff)
def save_project_on_staff_creation(sender, instance, created, **kwargs):
    instance.project_year.project.save()


@receiver(models.signals.post_delete, sender=ProjectYear)
def save_project_on_py_delete(sender, instance, **kwargs):
    instance.project.save()


@receiver(models.signals.post_save, sender=ProjectYear)
def save_project_on_py_creation(sender, instance, created, **kwargs):
    instance.project.save()


@receiver(models.signals.post_delete, sender=Review)
def save_project_year_on_review_delete(sender, instance, **kwargs):
    # if the py status is set to 3 (reviewed) it should be updated/downgraded to 2 (submitted)
    if instance.project_year.status == 3:
        py = instance.project_year
        py.status = 2
        py.save()


@receiver(models.signals.post_save, sender=Review)
def save_project_year_on_review_creation(sender, instance, created, **kwargs):
    py = instance.project_year
    # if the reviewer denied approval, project year status = denied
    if instance.approval_status == 0:
        py.status = 5
    # if the reviewer cancelled approval, project year status = cancelled
    elif instance.approval_status == 9:
        py.status = 9

    # if the reviewer approved, project year status = approved
    elif instance.approval_status == 1:
        py.status = 4

    # finally, if the py status happens to be set to 2 (submitted) it should be updated to 3 (reviewed)
    elif instance.project_year.status == 2:
        py.status = 3
    py.save()




@receiver(models.signals.pre_delete, sender=Project)
def delete_project_years_before_deleting_project(sender, instance, **kwargs):
    Staff.objects.filter(project_year__project=instance).delete()
