from .import models

def resave_all(samples = models.Sample.objects.all()):

    for s in samples:
        if s.date_deployed != None:
            my_sample = models.Sample.objects.get(id=s.id)
            my_sample.save()
