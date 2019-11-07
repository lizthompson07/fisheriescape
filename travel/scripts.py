from . import models

def resave_all(events = models.Trip.objects.all()):
    for obj in events:
        obj.save()
