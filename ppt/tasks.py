from celery import shared_task

from .models import DMA


@shared_task(name="resave_dmas")
def resave_dmas():
    for obj in DMA.objects.filter(status=1):
        obj.save()
