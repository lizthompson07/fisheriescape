from .import models

def resave_all(details = models.FishDetail.objects.all()):

    for d in details:
        detail = models.FishDetail.objects.get(pk = d.id)
        detail.save()
