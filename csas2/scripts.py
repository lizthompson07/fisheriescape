from csas2.models import CSASRequest

def resave_requests():
    for r in CSASRequest.objects.all():
        r.save()
from csas2.scripts import resave_requests
resave_requests()
