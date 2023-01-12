import os

from django.db import models
from django.dispatch import receiver

from .models import DMAReview


@receiver(models.signals.post_save, sender=DMAReview)
def save_project_year_on_review_save(sender, instance, created, **kwargs):
    instance.dma.save()


@receiver(models.signals.post_delete, sender=DMAReview)
def save_dma_on_review_delete(sender, instance, **kwargs):
    instance.dma.save()
