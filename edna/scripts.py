import csv
import datetime
import os

from django.conf import settings
from django.contrib.auth.models import User

from shared_models.models import Region, Province
from . import models



def export_fixtures():
    """ a simple function to expor the important lookup tables. These fixutre will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
    models_to_export = [
        models.FiltrationType,
        models.DNAExtractionProtocol,
    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w')
        myfile = File(f)
        myfile.write(data)
        myfile.close()


def resave_extracts():
    for e in models.DNAExtract.objects.all():
        e.save()