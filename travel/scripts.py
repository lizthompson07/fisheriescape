from . import models
from . import utils

def resave_all(events = models.Trip.objects.all()):
    for obj in events:
        utils.get_reviewers(obj)

