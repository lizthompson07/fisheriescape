import os

from django.core import serializers
from django.core.files import File

from . import models


def export_fixtures():
    """ a simple function to export the important lookup tables. These fixtures will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
    models_to_export = [
        models.LengthBin,
        models.Maturity,
    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w', encoding='utf-8')
        myfile = File(f)
        myfile.write(data)
        myfile.close()


def resave_samples(samples=models.Sample.objects.all()):
    for s in samples:
        s.save()


def resave_fish(fishies=models.FishDetail.objects.all()):
    for f in fishies:
        f.save()


def pop_herring():
    for s in models.Sample.objects.filter(species__isnull=True):
        s.species = models.Species.objects.get(aphia_id=126417)
        s.save()
