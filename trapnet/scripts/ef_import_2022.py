import csv
import datetime
import os

from django.conf import settings
from django.utils.timezone import get_current_timezone, make_aware

from lib.templatetags.custom_filters import nz
from shared_models.models import River, FishingArea, Province
from trapnet import models

rootdir = os.path.join(settings.BASE_DIR, 'trapnet', 'temp')


def get_efisher_lookup():
    # bring in the e-fishers as a dict:
    efisher_lookup = {None: None}
    with open(os.path.join(rootdir, 'summary EF gear index.csv'), 'r') as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            efisher_lookup[r["DFO data base code"]] = r["name of model"]
    return efisher_lookup


def run_spp_checks():
    # check if all the species codes are in the db
    with open(os.path.join(rootdir, 'Species_codes.csv'), 'r') as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            try:
                s = models.Species.objects.get(tsn=r["SPECIES_ITIS_CODE"])
            except models.Species.DoesNotExist:
                print(r["SPECIES_ITIS_CODE"], r["Common_name"], "does not exist in db")
                # create an entry in the species table provided it is not TSN = 0
                s = models.Species.objects.create(common_name_eng=r["Common_name"], tsn=r["SPECIES_ITIS_CODE"])


def run_river_checks():
    sfa15 = FishingArea.objects.get(name="SFA15")
    # Let's make sure we have all the rivers
    new_rivers = [
        dict(cgndb="DAVTC", name="Quigley brook", fishing_area=sfa15, parent_river=River.objects.get(cgndb="DALLK")),  # child of KED
        dict(cgndb="DARJS", name="Crooked rapids", fishing_area=sfa15, parent_river=River.objects.get(cgndb="DAPWI"))  # child of UPS
    ]
    for r in new_rivers:
        River.objects.get_or_create(**r)

    with open(os.path.join(rootdir, 'Site_data.csv'), 'r') as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            try:
                river = River.objects.get(cgndb=r["CGNDB"])
            except River.DoesNotExist:
                print(r["CGNDB"], r["RIVER_NAME"], r["CATCHMENT_NAME"], r["LATITUDE"], r["LONGITUDE"], r["SITE_FISHING_AREA_CODE"], "does not exist in db")

    # Let's make sure we have all the river sites entered
    ## the default is that none of these exist

    with open(os.path.join(rootdir, 'Site_data.csv'), 'r') as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            river = River.objects.get(cgndb=r["CGNDB"])
            name = r["SITE"]

            qs = models.RiverSite.objects.filter(name__iexact=name, river=river)
            if not qs.exists():
                kwargs = dict(
                    name=name,
                    river=river,
                    latitude=r["LATITUDE_NEW"] if r["LATITUDE_NEW"] != "NA" else r["LATITUDE"],
                    longitude=r["LONGITUDE_NEW"] if r["LONGITUDE_NEW"] != "NA" else r["LONGITUDE"],
                    province=Province.objects.get(abbrev_eng=r["RIVER_PROVINCE"]),
                    directions=nz(r["DIRECTIONS"], None),
                )
                models.RiverSite.objects.create(**kwargs)


def run_process_samples():
    efisher_lookup = get_efisher_lookup()

    # delete previously imported samples
    models.Sample.objects.filter(old_id__isnull=False).delete()

    # ok I think we are ready to tackle the sample
    with open(os.path.join(rootdir, 'problematic_site_data.csv'), 'w') as wf:
        writer = csv.writer(wf, delimiter=',', lineterminator='\n')
        with open(os.path.join(rootdir, 'Site_data.csv'), 'r') as f:
            csv_reader = csv.DictReader(f)
            writer.writerow(list(csv_reader.fieldnames) + ["DESCRIPTION OF PROBLEM"])

            for r in csv_reader:
                # clean the row
                for key in r:
                    r[key] = r[key].strip()  # remove any trailing spaces
                    if r[key] in ['', "NA"]:  # if there is a null value of any kind, replace with NoneObject
                        r[key] = None

                river = River.objects.get(cgndb=r["CGNDB"])
                site = models.RiverSite.objects.get(name__iexact=r["SITE"], river=river)
                raw_date = r["SITE_EVENT_DATE"]

                # only continue if there is a date
                if not raw_date:
                    writer.writerow([r[key] for key in r] + ["The record has no date time"])
                else:
                    raw_date = raw_date.split(" ")[0]
                    start_date = make_aware(datetime.datetime.strptime(f"{raw_date} 12:00", "%d/%m/%Y %H:%M"), get_current_timezone())
                    old_id = f"{start_date.year}{start_date.month}{start_date.day}{site.id}"

                    # only continue if this is not a duplicate sample
                    if models.Sample.objects.filter(old_id=old_id).exists():
                        writer.writerow([r[key] for key in r] + [
                            f"The record seems to be a duplicate entry: {start_date.year}-{start_date.month}-{start_date.day} @ site '{site}'"])
                    else:
                        efisher = efisher_lookup[r["ELECTROFISHER_TYPE"]]
                        if efisher:
                            efisher, created = models.Electrofisher.objects.get_or_create(name=efisher)
                        kwargs = {
                            "old_id": old_id,
                            "site": site,
                            "sample_type": 2,
                            "arrival_date": start_date,
                            "departure_date": start_date,
                            "percent_riffle": r["TOS1"],
                            "percent_run": r["TOS2"],
                            "percent_flat": r["TOS3"],
                            "percent_pool": r["TOS4"],
                            "electrofisher": efisher,
                            "bank_length_left": r["LENGTH_LEFT_BANK"],
                            "bank_length_right": r["LENGTH_RIGHT_BANK"],
                        }

                        models.Sample.objects.create(**kwargs)

                        # "samplers"
                        # "notes"
                        # "crew_probe"
                        # "crew_seine"
                        # "crew_dipnet"
                        # "crew_extras"
                        # "width_lower"
                        # "depth_1_lower"
                        # "depth_2_lower"
                        # "depth_3_lower"
                        # "width_middle"
                        # "depth_1_middle"
                        # "depth_2_middle"
                        # "depth_3_middle"
                        # "width_upper"
                        # "depth_1_upper"
                        # "depth_2_upper"
                        # "depth_3_upper"
                        # "max_depth"
                        # "air_temp_arrival"
                        # "min_air_temp"
                        # "max_air_temp"
                        # "percent_cloud_cover"
                        # "precipitation_category"
                        # "precipitation_comment"
                        # "wind_speed"
                        # "wind_direction"
                        # "water_depth_m"
                        # "water_level_delta_m"
                        # "discharge_m3_sec"
                        # "water_temp_c"
                        # "water_temp_trap_c"
                        # "water_cond"
                        # "overhanging_veg_left"
                        # "overhanging_veg_right"
                        # "max_overhanging_veg_left"
                        # "max_overhanging_veg_right"
                        # "percent_fine"
                        # "percent_sand"
                        # "percent_gravel"
                        # "percent_pebble"
                        # "percent_cobble"
                        # "percent_rocks"
                        # "percent_boulder"
                        # "percent_bedrock"
                        # "site_type"
                        # "electrofisher"
                        # "electrofisher_voltage"
                        # "electrofisher_output_low"
                        # "electrofisher_output_high"
                        # "electrofisher_frequency"
                        # "electrofisher_pulse_type"
                        # "duty_cycle":123
                    # }


def run_process_fish():
    with open(os.path.join(rootdir, 'problematic_fish_data.csv'), 'w') as wf:
        writer = csv.writer(wf, delimiter=',', lineterminator='\n')

        with open(os.path.join(rootdir, 'fish_data.csv'), 'r') as f:
            csv_reader = csv.DictReader(f)
            writer.writerow(list(csv_reader.fieldnames) + ["DESCRIPTION OF PROBLEM"])

            for r in csv_reader:
                # clean the row
                for key in r:
                    r[key] = r[key].strip()  # remove any trailing spaces
                    if r[key] in ['', "NA"]:  # if there is a null value of any kind, replace with NoneObject
                        r[key] = None

                raw_date = r["SITE_EVENT_DATE"]
                # only continue if there is a date
                if raw_date:
                    raw_date = raw_date.split(" ")[0]
                    start_date = make_aware(datetime.datetime.strptime(f"{raw_date} 12:00", "%d/%m/%Y %H:%M"), get_current_timezone())
                    catchment_index = r["CATCHMENT_INDEX"]

                    sfa = "SFA15" if catchment_index == "1" else "SFA16"

                    # ok let's see if we can find a sample
                    qs = models.Sample.objects.filter(
                        site__name__iexact=r["SITE"],
                        site__river__fishing_area__name__iexact=sfa,
                        arrival_date=start_date
                    )

                    if not qs.exists():
                        # does the site even exist?
                        qs = models.RiverSite.objects.filter(
                            name__iexact=r["SITE"],
                            river__fishing_area__name__iexact=sfa,
                        )
                        if not qs.exists():
                            writer.writerow([r[key] for key in r] + [f"There is no record of site '{r['SITE']}' in {sfa}"])
                        else:
                            writer.writerow([r[key] for key in r] + [
                                f"There is no record of site '{r['SITE']}' in {sfa} being sampled on {start_date.strftime('%Y-%m-%d')}"])

                    elif qs.count() > 1:
                        writer.writerow([r[key] for key in r] + ["There is more than one site with same name being sampled on the same date!"])

                else:
                    writer.writerow([r[key] for key in r] + ["Fish observation has no date/time"])


def process_master_files(process_samples=False, process_fish=False, skip_checks=False):
    if skip_checks:
        run_spp_checks()
        run_river_checks()

    if process_samples:
        print("PROCESSING SITE DATA")
        run_process_samples()

    if process_fish:
        print("PROCESSING FISH DATA")
        run_process_fish()
