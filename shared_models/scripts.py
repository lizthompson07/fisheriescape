import os

from django.core import serializers
from django.core.files import File
import uuid
from .import models

def save_and_add_uuid():
    model_list = [models.Region, models.Branch, models.Division, models.Section, models.Province]

    for model in model_list:
        for obj in model.objects.all():
            if not obj.uuid:
                obj.uuid = uuid.uuid4()
                obj.save()


def pad_codes():
    for port in models.Port.objects.all():
        if len(port.district_code) == 1:
            port.district_code = "0{}".format(port.district_code)
            port.save()
        if len(port.port_code) == 1:
            port.port_code = "0{}".format(port.port_code)
            port.save()


def export_fixtures():
    """ a simple function to expor the important lookup tables. These fixutre will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
    models_to_export = [
        models.FiscalYear,
    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w')
        myfile = File(f)
        myfile.write(data)
        myfile.close()

