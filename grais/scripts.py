from .import models

def resave_all(sample = models.Sample.objects.all()):

    for obj in sample:
        obj.save()
