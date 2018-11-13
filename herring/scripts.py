from .import models

def resave_samples(samples = models.Sample.objects.all()):
    for s in samples:
        s.save()


def resave_fish(fishies = models.FishDetail.objects.all()):
    for f in fishies:
        f.save()
