import csv
import datetime
import json
import os

from django.contrib.gis.geos import Point
from django.utils import timezone
from django.core import serializers

from fisheriescape import models


# to get list of url names from rest api
# To use in shell:
# from fisheriescape.scripts import print_url_pattern_names
# from fisheriescape.api import urls
# print_url_pattern_names(urls.urlpatterns)

def print_url_pattern_names(patterns):
    """Print a list of urlpattern and their names"""
    for pat in patterns:
        if pat.__class__.__name__ == 'URLResolver':  # load patterns from this URLResolver
            print_url_pattern_names(pat.url_patterns)
        elif pat.__class__.__name__ == 'URLPattern':  # load name from this URLPattern
            if pat.name is not None:
                print('[API-URL] {:>50} -> {}'.format(pat.name, pat.pattern))


# for individual exports, can use:
# python manage.py dumpdata app_name.model_name > fisheriescape/fixtures/file.json

# to run this script do:
# python manage.py shell
# from fisheriescape.scripts import export_fixtures
# export_fixtures()


def export_fixtures():
    """ a simple function to export the important lookup tables. These fixtures will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

    models_to_export = [
        models.FisheryArea,
        models.NAFOArea,
        models.Hexagon,
        models.Fishery,
        models.Species,
        models.MarineMammal,
        models.Mitigation,
        models.Week,

    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        parsed = json.loads(data)
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w', encoding='utf-8')
        f.write(json.dumps(parsed, indent=4, sort_keys=True))
        f.close()


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


## this can be used to parse import of M2M fields -- currently using for marine_mammals field
def many_var(row_name, instance_name, model_name):
    if row_name != "" and row_name:
        tmp_arr = row_name.split(';')
        print(tmp_arr)
        for tmp in tmp_arr:
            tmp_obj, _ = model_name.objects.get_or_create(english_name=tmp.strip())
            instance_name.add(int(tmp_obj.id))
        return
    else:
        return


## this can be used to parse import of M2M fields -- currently using for mitigation_type field
def many_var_mit(row_name, instance_name, model_name):
    if row_name != "" and row_name:
        tmp_arr = row_name.split(';')
        print(tmp_arr)
        for tmp in tmp_arr:
            tmp_obj, _ = model_name.objects.get_or_create(mitigation_type=tmp.strip())
            instance_name.add(int(tmp_obj.id))
        return
    else:
        return


## this can be used to parse import of M2M fields -- currently using for mitigation_type field
def many_var_fish(row_name, instance_name, model_name):
    if row_name != "" and row_name:
        tmp_arr = row_name.split(';')
        print(tmp_arr)
        for tmp in tmp_arr:
            tmp_obj, _ = model_name.objects.get_or_create(name=tmp.strip())
            instance_name.add(int(tmp_obj.id))
        return
    else:
        return


def import_fishery_info():
    """ a simple function to import information from a csv """
    csv_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'data', 'fishery info import.csv'),
    )
    cont_success = 0
    # Remove all data from Table
    models.Fishery.objects.all().delete()

    with open(csv_file, newline='', encoding='UTF-8') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        # next(spamreader, None)  # skip the headers
        print('Loading...')
        # for row in spamreader:
        #     print(row[0])
        for row in spamreader:

            # to get dates with timezone settings
            start_date = timezone.datetime(int(row["Year start"]), int(row["Month start"]), int(row["Day start"]),
                                           tzinfo=timezone.get_current_timezone())
            end_date = timezone.datetime(int(row["Year end"]), int(row["Month end"]), int(row["Day end"]),
                                         tzinfo=timezone.get_current_timezone())

            # Get or create FK fields first
            species_obj, created = models.Species.objects.get_or_create(
                english_name=row["Species"].strip()
            )

            # main logic for regular field types -- for FK get it first
            created, _ = models.Fishery.objects.get_or_create(
                species=species_obj,
                participants=row["Participants"].strip(),
                participant_detail=row["Participant detail"].strip(),
                start_date=start_date,
                end_date=end_date,
                fishery_status=row["Fishery Status"].strip(),
                license_type=row["Type of License"].strip(),
                management_system=row["Management System"].strip(),
                fishery_comment=row["General comments"].strip(),
                gear_type=row["Gear Type"].strip(),
                gear_amount=row["Average Gear Amount/Participant"].strip(),
                gear_config=row["Gear Configuration"].strip(),
                gear_soak=row["Avg Rope Soak time (hrs)"].strip(),
                gear_primary_colour=row["Gear Primary Colour"].strip(),
                gear_secondary_colour=row["Gear Secondary Colour"].strip(),
                gear_tertiary_colour=row["Gear Tertiary Colour"].strip(),
                gear_comment=row["Gear Comment"].strip(),
                monitoring_aso=row["ASO %"].strip(),
                monitoring_dockside=row["Dockside %"].strip(),
                monitoring_logbook=row["Logbook %"].strip(),
                monitoring_vms=row["VMS %"].strip(),
                monitoring_comment=row["Monitoring Comment"].strip(),
                mitigation_comment=row["Mitigation comments"].strip(),
            )

            # add in M2M fields after created
            if row["AreaID"].strip():
                many_var_fish(row["AreaID"], created.fishery_areas, models.FisheryArea)

            if row["Mitigation Type"].strip():
                many_var_mit(row["Mitigation Type"], created.mitigation, models.Mitigation)

            if row["Marine Mammals"].strip():
                many_var(row['Marine Mammals'], created.marine_mammals, models.MarineMammal)

            cont_success += 1
        print(f'{str(cont_success)} records inserted successfully! ')


def import_scores_info_from_file_path(path: str) -> dict:
    """ a simple function to import information from a csv """
    csv_file = path

    with open(csv_file, newline='', encoding='UTF-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        print(f"Importing file {csv_file}...")
        result = import_scores_from_reader(reader=reader)

        print(f"✅ {result.get('count_success')} records inserted successfully! for file {csv_file}")
        print(f"❌ {len(result.get('errors'))} errors for file {csv_file}")

        return result


def import_all_scores(folder_path: str) -> dict:
    result = {
        "count_success": 0,
        "errors": []
    }
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            file_result = import_scores_info_from_file_path(path=file_path)
            result["count_success"] += file_result["count_success"]
            result["errors"] += file_result["errors"]
    return result


def import_vulnerable_species_spots_from_file_path(file_path: str) -> dict:
    print(f"Importing file {file_path}...")

    with open(file_path, newline='', encoding='UTF-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        result = import_vulnerable_species_from_reader(reader=reader)
        print(f"✅ {result.get('count_success')} records inserted successfully! for file {file_path}")
        print(f"❌ {len(result.get('errors'))} errors for file {file_path}")

    return result


def import_all_vulnerable_species_spots(folder_path: str) -> dict:
    result = {
        "count_success": 0,
        "errors": []
    }
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            file_result = import_vulnerable_species_spots_from_file_path(file_path=file_path)
            result["count_success"] += file_result["count_success"]
            result["errors"] += file_result["errors"]

    return result


def import_vulnerable_species_from_reader(reader: csv.DictReader) -> dict:
    count_success = 0
    errors = []
    for row in reader:
        try:
            vulnerable_species_english_name = row["species"].strip().capitalize()
            vulnerable_species_obj, created = models.VulnerableSpecies.objects.get_or_create(
                defaults={'english_name': vulnerable_species_english_name},
                english_name__iexact=vulnerable_species_english_name
            )

            week_obj, created = models.Week.objects.get_or_create(
                week_number=row["SW"].strip()
            )

            created, _ = models.VulnerableSpeciesSpot.objects.get_or_create(
                vulnerable_species=vulnerable_species_obj,
                week=week_obj,
                count=row["number"].strip(),
                date=datetime.datetime.strptime(row["date"].strip(), '%m/%d/%Y').date(),
                point=Point(float(row["lat"].strip()), float(row["lon"].strip())),
            )

            count_success += 1
        except Exception as e:
            errors.append(f"❌ error inserting line {row} : {e}")

    return {
        "count_success": count_success,
        "errors": errors,
    }


def import_scores_from_reader(reader: csv.DictReader) -> dict:
    count_success = 0
    errors = []
    for row in reader:
        try:
            # Get or create FK fields first
            hexagon_obj, created = models.Hexagon.objects.get_or_create(
                grid_id=str(row["grid.id"].strip())
            )

            species_obj, created = models.Species.objects.get_or_create(
                defaults={'english_name': str(row["sw2"].strip()[:-19].strip())},
                english_name__iexact=str(row["sw2"].strip()[:-19].strip())
            )

            week_obj, created = models.Week.objects.get_or_create(
                week_number=row["sw"].strip()
            )
            created, _ = models.Score.objects.get_or_create(
                hexagon=hexagon_obj,
                species=species_obj,
                week=week_obj,
                site_score=row["ss.std"].strip(),
                ceu_score=row["ceu"].strip(),
                fs_score=row["fs"].strip(),
            )
            count_success += 1
        except Exception as e:
            errors.append(f"❌ error inserting line {row} : {e}")

    return {
        "count_success": count_success,
        "errors": errors
    }
