import os
import json

from django.core import serializers


# models_to_export is an array of models fed in from the shell script running this command.
# output dir is the directory to output the fixtures to, if None fixtures will be created
# in the scripts directory
#
# from scripts import model_export
# from maret import models
#
# models_to_export = [models.Interaction, models.Committee]
# model_export.export_fixtures(modesl_to_export, r'./maret/fixtures/)
def export_fixtures(models_to_export, output_path=None):

    """ a simple function to export the important lookup tables. These fixtures will be used for testing and also for
    seeding new instances"""
    if not output_path:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        parsed = json.loads(data)
        my_label = model._meta.db_table
        f = open(os.path.join(output_path, f'{my_label}.json'), 'w', encoding='utf-8')
        f.write(json.dumps(parsed, indent=4, sort_keys=True))
        f.close()