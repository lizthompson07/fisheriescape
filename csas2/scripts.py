from csas2.models import CSASRequest

def resave_requests():
    for r in CSASRequest.objects.all():
        r.save()