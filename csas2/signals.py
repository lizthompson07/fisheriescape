import os

from django.db import models
from django.dispatch import receiver

from csas2.models import CSASRequestReview, CSASRequestFile, Process, MeetingFile, Document, DocumentTracking, Meeting, TermsOfReference


@receiver(models.signals.post_save, sender=CSASRequestReview)
def save_request_on_review_save(sender, instance, created, **kwargs):
    instance.csas_request.save()


@receiver(models.signals.post_save, sender=CSASRequestFile)
def save_request_on_file_save(sender, instance, created, **kwargs):
    instance.csas_request.save()


@receiver(models.signals.post_save, sender=Process)
def save_requests_on_process_save(sender, instance, created, **kwargs):
    for r in instance.csas_requests.all():
        r.save()


# @receiver(models.signals.m2m_changed, sender=Process.csas_requests.through)
# def csas_request_change(sender, action, pk_set, instance=None, **kwargs):
#     """This will save process instance if any of its attached requests are update"""
#     instance.save()


# @receiver(models.signals.post_delete, sender=CSASRequest)
# def update_process_on_request_delete(sender, instance, **kwargs):
#     for p in instance.processes.all():
#         p.save()
#
#
# @receiver(models.signals.post_save, sender=CSASRequest)
# def update_process_on_request_change_or_create(sender, instance, **kwargs):
#     for p in instance.processes.all():
#         p.save()


# @receiver(models.signals.post_save, sender=Process)
# def update_request_on_process_change_or_create(sender, instance, **kwargs):
#     for r in instance.csas_requests.all():
#         r.save()


@receiver(models.signals.post_save, sender=Meeting)
def save_process_on_meeting_save(sender, instance, created, **kwargs):
    instance.process.save()


@receiver(models.signals.post_save, sender=Document)
def save_process_on_doc_save(sender, instance, created, **kwargs):
    instance.process.save()


@receiver(models.signals.post_save, sender=DocumentTracking)
def save_process_on_doc_tracking_save(sender, instance, created, **kwargs):
    instance.document.process.save()


@receiver(models.signals.post_save, sender=TermsOfReference)
def save_process_on_tor_save(sender, instance, created, **kwargs):
    instance.process.save()


@receiver(models.signals.post_delete, sender=CSASRequestFile)
def auto_delete_csas2_request_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
    instance.csas_request.save()


@receiver(models.signals.pre_save, sender=CSASRequestFile)
def auto_delete_csas2_request_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = CSASRequestFile.objects.get(pk=instance.pk).file
    except CSASRequestFile.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(models.signals.post_delete, sender=MeetingFile)
def auto_delete_csas2_meeting_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=MeetingFile)
def auto_delete_csas2_meeting_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = MeetingFile.objects.get(pk=instance.pk).file
    except MeetingFile.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(models.signals.post_save, sender=DocumentTracking)
def save_docuemnt_on_tracking_save(sender, instance, created, **kwargs):
    instance.document.save()


@receiver(models.signals.post_delete, sender=Document)
def auto_delete_csas2_meeting_file_on_delete(sender, instance, **kwargs):
    if instance.file_en:
        if os.path.isfile(instance.file_en.path):
            os.remove(instance.file_en.path)

    if instance.file_fr:
        if os.path.isfile(instance.file_fr.path):
            os.remove(instance.file_fr.path)


@receiver(models.signals.pre_save, sender=Document)
def auto_delete_csas2_meeting_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_doc = Document.objects.get(pk=instance.pk)
    except Document.DoesNotExist:
        return False

    old_file = old_doc.file_en
    new_file = instance.file_en
    if old_file.name and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

    old_file = old_doc.file_fr
    new_file = instance.file_fr
    if old_file.name and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
