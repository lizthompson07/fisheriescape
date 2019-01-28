from . import models


def resave_all(objects=models.Transaction.objects.all()):
    for t in objects:
        t.save()
