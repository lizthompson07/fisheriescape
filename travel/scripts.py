from . import models

def resave_all(events = models.Event.objects.all()):
    for obj in events:
        obj.save()
