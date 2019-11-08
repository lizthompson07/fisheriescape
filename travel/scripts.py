from . import models
from . import utils

def resave_all(events = models.Trip.objects.all()):
    for obj in events:
        if obj.status_id == 8:
            obj.reviewers.all().delete()
            utils.get_reviewers(obj)

