import csv
import datetime
import os
import statistics

from django.conf import settings
from django.utils.timezone import get_current_timezone, make_aware

from lib.functions.custom_functions import listrify
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
                print(r["SITE"], r["CGNDB"], r["RIVER_NAME"], r["CATCHMENT_NAME"], r["LATITUDE"], r["LONGITUDE"], r["SITE_FISHING_AREA_CODE"], "does not exist in db")

    # Let's make sure we have all the river sites entered
    ## the default is that none of these exist

    with open(os.path.join(rootdir, 'Site_data.csv'), 'r') as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            for key in r:
                r[key] = r[key].strip()  # remove any trailing spaces
                if r[key] in ['', "NA"]:  # if there is a null value of any kind, replace with NoneObject
                    r[key] = None
            try:
                river = River.objects.get(cgndb=r["CGNDB"])
            except River.MultipleObjectsReturned:
                print(f"There were multiple hits for river with CGNDB: {r['CGNDB']}")
            else:
                name = r["SITE"]

                qs = models.RiverSite.objects.filter(name__iexact=name, river=river)
                if not qs.exists():
                    print(r["RIVER_PROVINCE"])
                    kwargs = dict(
                        name=name,
                        river=river,
                        latitude=r["LATITUDE_NEW"] if r["LATITUDE_NEW"] != "NA" else r["LATITUDE"],
                        longitude=r["LONGITUDE_NEW"] if r["LONGITUDE_NEW"] != "NA" else r["LONGITUDE"],
                        province=Province.objects.get(abbrev_eng=r["RIVER_PROVINCE"]) if r["RIVER_PROVINCE"] else None,
                        directions=nz(r["DIRECTIONS"], None),
                    )
                    models.RiverSite.objects.create(**kwargs)


def add_note(notes, key, value):
    mystr = str()
    if len(notes):
        mystr += "\n\n"
    if key and value:
        mystr += f"{key}: {value}"
    else:
        mystr += f"{key}"
    notes += mystr
    return notes


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

                notes = str()  # start over with a blank string for notes

                try:
                    river = River.objects.get(cgndb=r["CGNDB"])
                except (River.DoesNotExist, River.MultipleObjectsReturned) as e:
                    print(f"cannot create sample: temp id = {r['TEMP_SAMPLE_ID']}, {e}")
                else:
                    site = models.RiverSite.objects.get(name__iexact=r["SITE"], river=river)
                    raw_date = r["SITE_EVENT_DATE"]

                    # only continue if there is a date
                    if not raw_date:
                        writer.writerow([r[key] for key in r] + ["The record has no date time"])
                    else:
                        raw_date = raw_date.split(" ")[0]
                        start_date = make_aware(datetime.datetime.strptime(f"{raw_date} 12:00", "%d/%m/%Y %H:%M"), get_current_timezone())
                        old_id = r["TEMP_SAMPLE_ID"]

                        # only continue if this is not a duplicate sample
                        if models.Sample.objects.filter(old_id=old_id).exists():
                            writer.writerow([r[key] for key in r] + [
                                f"The record seems to be a duplicate: {start_date.year}-{start_date.month}-{start_date.day} @ site {site}"])
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
                                "width_lower": r["WIDTH_LOWER"],
                                "width_middle": r["WIDTH_MIDDLE"],
                                "width_upper": r["WIDTH_UPPER"],
                                "depth_1_lower": r["DEPTHA1"],
                                "depth_2_lower": r["DEPTHA2"],
                                "depth_3_lower": r["DEPTHA3"],
                                "depth_1_middle": r["DEPTHB1"],
                                "depth_2_middle": r["DEPTHB2"],
                                "depth_3_middle": r["DEPTHB3"],
                                "depth_1_upper": r["DEPTHC1"],
                                "depth_2_upper": r["DEPTHC2"],
                                "depth_3_upper": r["DEPTHC3"],
                                "max_depth": r["DEPTH_MAX"],
                                "air_temp_arrival": r["AIR_TEMPERATURE"],
                                "water_cond": r["WATER_CONDUCTIVITY"],
                                "water_ph": r["WATER_PH"],

                                "percent_fine": r["SUB_TYPE_FINES"],
                                "percent_sand": r["SUB_TYPE_SAND"],
                                "percent_gravel": r["SUB_TYPE_GRAVEL"],
                                "percent_pebble": r["SUB_TYPE_PEBBLE"],
                                "percent_cobble": r["SUB_TYPE_COBBLE"],
                                "percent_rocks": r["SUB_TYPE_ROCKS"],
                                "percent_boulder": r["SUB_TYPE_BOULDER"],
                                "percent_bedrock": r["SUB_TYPE_BEDROCK"],
                                "overhanging_veg_left": r["L_BK_OVERHANGING_VEG"],
                                "overhanging_veg_right": r["R_BK_OVERHANGING_VEG"],
                                "max_overhanging_veg_left": r["MAX_OVERHANG_L_BK"],
                                "max_overhanging_veg_right": r["MAX_OVERHANG_R_BK"],
                                "electrofisher_voltage": r["ELECTROFISHER_FREQUENCY"],
                                "electrofisher_frequency": r["ELECTROFISHER_VOLTAGE"],
                                "site_type": 2 if r["BARRIER_PRESENT"] else 1,
                                "crew_probe": r["CREW_PROBE"],
                                "crew_seine": r["CREW_SEINE"],
                                "crew_dipnet": r["CREW_DIPNET"],
                                "seine_type": r["APRONSEINE_TYPE"],
                            }

                            # deal with the extra samplers
                            extras = str()
                            if r["CREW_BUCKET"]:
                                extras = f'BUCKET: {r["CREW_BUCKET"]} / '
                            if r["CREW_RECORDER"]:
                                extras = f'RECORDER: {r["CREW_RECORDER"]} / '
                            others = [
                                r["CREW_OTHER1"],
                                r["CREW_OTHER2"],
                                r["CREW_OTHER3"],
                                r["CREW_OTHER4"],
                                r["CREW_OTHER5"],
                            ]
                            while None in others: others.remove(None)
                            if len(others):
                                extras = f'OTHERS: {listrify(others)}'

                            if extras.endswith(" / "):
                                extras = extras[:-3]
                            kwargs["crew_extras"] = extras

                            # there is a bit of a pickle concerning efisher current / output
                            # in the masterfile, there are two columns, CURRENT and OUTPUT. It is not clear what the differences are between these two.
                            # it seems like output column sometimes contains some arbitrary measure of power that is associated with a particular electrofisher
                            # and other times it contains things that look like amps (e.g. < 5)
                            # finally, in modern times we collect two values (high and low) but here we will have only 1 value. accordingly, we will use this value to populate both fields
                            output = None
                            if r["ELECTROFISHER_CURRENT"]:
                                output = r["ELECTROFISHER_CURRENT"]
                            elif r["ELECTROFISHER_OUTPUT"] and float(r["ELECTROFISHER_OUTPUT"]) < 5:
                                output = r["ELECTROFISHER_OUTPUT"]

                            kwargs["electrofisher_output_low"] = output
                            kwargs["electrofisher_output_high"] = output

                            # water temp can be a bit complicated because the masterlist has many measurements but we will be taking just one in dmapps
                            # we will take an average of all measurements
                            temps = [
                                r["WATER_TEMPERATURE_ARRIVAL"],
                                r["WATER_TEMPERATURE_DEPART"],
                                r["WATER_TEMP1"],
                                r["WATER_TEMP2"],
                                r["WATER_TEMP3"],
                            ]
                            while None in temps: temps.remove(None)
                            while 0 in temps: temps.remove(0)

                            if len(temps):
                                kwargs["water_temp_c"] = statistics.mean([float(t) for t in temps])
                                if len(temps) > 1:
                                    notes = add_note(notes, "WATER TEMPERATURE",
                                                 f"The mean of the following water temperature measurements were used: {listrify(temps)}")



                            # there is no field for DEPTH_LAYOUT_TYPE in dmapps, so we will just make a note
                            if r["DEPTH_LAYOUT_TYPE"]:
                                notes = add_note(notes, "DEPTH_LAYOUT_TYPE", r["DEPTH_LAYOUT_TYPE"])

                            # there is no field for MESH_SIZE in dmapps, so we will just make a note
                            if r["MESH_SIZE"]:
                                notes = add_note(notes, "MESH_SIZE", r["MESH_SIZE"])

                            # append any remarks from the masterfile
                            if r["REMARK"]:
                                notes = add_note(notes, "ADDITIONAL REMARKS", r["REMARK"])

                            if len(notes):
                                kwargs["notes"] = notes

                            models.Sample.objects.create(**kwargs)

                            #now that we have a sample, it is time to deal with sweeps


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
                        # LIFE IS GOOD - CONTINUE !!
                        sample = qs.first()
                        # Now to deal with the sweep






                else:
                    writer.writerow([r[key] for key in r] + ["Fish observation has no date/time"])


def process_master_files(process_samples=False, process_fish=False, skip_checks=False):
    if not skip_checks:
        run_spp_checks()
        run_river_checks()

    if process_samples:
        print("PROCESSING SITE DATA")
        run_process_samples()

    if process_fish:
        print("PROCESSING FISH DATA")
        run_process_fish()
