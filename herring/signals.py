from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FishDetail

@receiver(post_save, sender=FishDetail)
def run_post_save_fish_detail(sender, instance, created, **kwargs):
    sample = instance.sample
    sample.save()

