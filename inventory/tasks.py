from celery import shared_task

from .models import Resource


@shared_task(name="resave_dmas")
def resave_resource_reviews():
    for obj in Resource.objects.filter(review_status=1):
        obj.save()
