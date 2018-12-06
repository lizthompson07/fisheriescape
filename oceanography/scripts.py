from .import models

def resave_missions(objects = models.Mission.objects.all()):
    for obj in objects:
        obj.save()

def resave_bottles():
    objects = models.Bottle.objects.filter(mission_id=8)
    for obj in objects:
        obj.save()
