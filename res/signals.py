import os

from django.db import models
from django.dispatch import receiver

from .models import Recommendation


@receiver(models.signals.post_save, sender=Recommendation)
def save_recommendation_on_application_save(sender, instance, created, **kwargs):
    instance.application.save()

