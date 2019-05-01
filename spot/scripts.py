from . import models

def resave_all(entries = models.Entry.objects.all()):
    for obj in entries:
        obj.save()
