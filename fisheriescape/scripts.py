import csv
import os

from django.conf import settings
from django.core import serializers
from django.core.files import File

from fisheriescape import models


# for individual exports, can use:
# python manage.py dumpdata app_name.model_name > fisheriescape/fixtures/file.json

#to run this script do:
# python manage.py shell
# from fisheriescape.scripts import export_fixtures
# export_fixtures()

def export_fixtures():
    """ a simple function to export the important lookup tables. These fixtures will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
    models_to_export = [
        models.FisheryArea,
        models.Species,
        models.MarineMammal,

    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w', encoding='utf-8')
        myfile = File(f)
        myfile.write(data)
        myfile.close()


def import_marine_mammals():
    """ a simple function to import information from a csv """
    csv_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'data', 'MM and Turtle info for possible interactions.csv'),
    )
    cont_success = 0
    # Remove all data from Table
    models.MarineMammal.objects.all().delete()

    with open(csv_file, newline='', encoding='latin1') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)  # skip the headers
        print('Loading...')
        # for row in spamreader:
        #     print(row[0])
        for row in spamreader:
            models.MarineMammal.objects.get_or_create(
                english_name=row[1],
                english_name_short=row[2],
                french_name=row[3],
                french_name_short=row[4],
                latin_name=row[5],
                population=row[6],
                sara_status=row[7],
                cosewic_status=row[8],
                website=row[9],
            )
            cont_success += 1
        print(f'{str(cont_success)} inserted successfully! ')
