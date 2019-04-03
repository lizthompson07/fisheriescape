from .import models


def resave_all():
    for obj in models.GCSample.objects.all():
        obj.save()

