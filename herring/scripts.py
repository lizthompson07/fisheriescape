from .import models

def resave_samples(samples = models.Sample.objects.all()):
    for s in samples:
        s.save()


def resave_fish(fishies = models.FishDetail.objects.all()):
    for f in fishies:
        f.save()


def pop_herring():
    for s in models.Sample.objects.filter(species__isnull=True):
        s.species = models.Species.objects.get(aphia_id=126417)
        s.save()