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
    models.Species.objects.get_or_create(common_name_eng="Splake")

    with open(os.path.join(rootdir, 'Species_codes.csv'), 'r') as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            try:
                s = models.Species.objects.get(tsn=r["SPECIES_ITIS_CODE"])
            except models.Species.DoesNotExist:
                if r["SPECIES_ITIS_CODE"] and r["SPECIES_ITIS_CODE"] != "" and r["SPECIES_ITIS_CODE"] != "0":
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
                print(r["SITE"], r["CGNDB"], r["RIVER_NAME"], r["CATCHMENT_NAME"], r["LATITUDE"], r["LONGITUDE"], r["SITE_FISHING_AREA_CODE"],
                      "does not exist in db")

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


def add_note(notes, key, value=None):
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
    from alive_progress import alive_bar

    efisher_lookup = get_efisher_lookup()

    # delete previously imported samples
    models.Sample.objects.filter(old_id__istartswith="gd").delete()
    mp1 = models.MonitoringProgram.objects.get(pk=1)
    mp2 = models.MonitoringProgram.objects.get(pk=2)

    # ok I think we are ready to tackle the sample
    with open(os.path.join(rootdir, 'problematic_site_data.csv'), 'w') as wf:
        writer = csv.writer(wf, delimiter=',', lineterminator='\n')

        with open(os.path.join(rootdir, 'Site_data.csv'), 'r') as f:
            row_count = sum(1 for row in csv.reader(f)) - 1

        with open(os.path.join(rootdir, 'Site_data.csv'), 'r') as f:
            csv_reader = csv.DictReader(f)
            writer.writerow(list(csv_reader.fieldnames) + ["DESCRIPTION OF PROBLEM"])
            with alive_bar(row_count, force_tty=True) as bar:  # declare your expected total
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
                            old_id = f'GD_{r["GD_ID"]}'

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
                                    "monitoring_program": mp1,
                                    "created_by_id": 50,
                                    "updated_by_id": 50,
                                }

                                # deal with seine type
                                seine_type = r["APRONSEINE_TYPE"]
                                if not seine_type:
                                    remarks = r["REMARK"]
                                    if remarks:
                                        remarks = remarks.lower()
                                        if "seine" in remarks and ("one man" in remarks or "1 man" in remarks):
                                            seine_type = 1
                                kwargs["seine_type"] = seine_type

                                # deal with didymo
                                didymo = None
                                remarks = r["REMARK"]
                                if remarks:
                                    remarks = remarks.lower()
                                    if "didymo" in remarks:
                                        if "present" in remarks or "high presence" in remarks or "didymo pom pom" in remarks:
                                            didymo = 1
                                        elif "absent" in remarks:
                                            didymo = 0
                                kwargs["didymo"] = didymo

                                # deal with the crew fields

                                # there will be two different approaches, depending on the catchment and the year.
                                # specifically on the Restigouche, beginning in 2009 a convention was adopted that the prober was identified using an
                                # asterix next to their name.
                                if "resti" in r["CATCHMENT_NAME"].lower() and int(r["SURVEY"]) >= 2009:
                                    crew_probe = None
                                    crew_seine = None
                                    crew_dipnet = None
                                    crew_extras = None
                                    # make a list of all the sampler names:
                                    total_crew = [
                                        r["CREW_OTHER1"],
                                        r["CREW_OTHER2"],
                                        r["CREW_OTHER3"],
                                        r["CREW_OTHER4"],
                                        r["CREW_OTHER5"],
                                        r["CREW_PROBE"],
                                        r["CREW_SEINE"],
                                        r["CREW_DIPNET"],
                                        r["CREW_BUCKET"],
                                        r["CREW_RECORDER"],
                                    ]
                                    while None in total_crew: total_crew.remove(None)
                                    if len(total_crew):
                                        prober = None
                                        for sampler in total_crew:
                                            if "*" in sampler:
                                                # remove that sampler from the total list
                                                total_crew.remove(sampler)
                                                # clean up the name of the sampler
                                                prober = sampler.replace("*", "").strip()
                                                # end the loop
                                                break
                                        crew_probe = prober
                                        crew_extras = f'{listrify(total_crew)}'
                                else:
                                    crew_probe = r["CREW_PROBE"]
                                    crew_seine = r["CREW_SEINE"]
                                    crew_dipnet = r["CREW_DIPNET"]
                                    crew_extras = None
                                    extras = str()

                                    if r["CREW_BUCKET"]:
                                        extras = f'{r["CREW_BUCKET"]} (bucket) / '
                                    if r["CREW_RECORDER"]:
                                        extras = f'{r["CREW_RECORDER"]} (recorder) / '
                                    others = [
                                        r["CREW_OTHER1"],
                                        r["CREW_OTHER2"],
                                        r["CREW_OTHER3"],
                                        r["CREW_OTHER4"],
                                        r["CREW_OTHER5"],
                                    ]
                                    while None in others: others.remove(None)
                                    if len(others):
                                        extras = f'{listrify(others)} (others)'

                                    if extras.endswith(" / "):
                                        extras = extras[:-3]

                                    if len(extras):
                                        crew_extras = extras

                                kwargs["crew_probe"] = crew_probe
                                kwargs["crew_seine"] = crew_seine
                                kwargs["crew_dipnet"] = crew_dipnet
                                kwargs["crew_extras"] = crew_extras

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

                                sample_kwargs = dict()
                                ef_kwargs = dict()

                                sample_fields = [f.name for f in models.Sample._meta.fields]
                                for key in kwargs:
                                    if key in sample_fields:
                                        sample_kwargs[key] = kwargs[key]
                                    else:
                                        ef_kwargs[key] = kwargs[key]

                                sample = models.Sample.objects.create(**sample_kwargs)
                                ef_sample = sample.ef_sample
                                for key in ef_kwargs:
                                    setattr(ef_sample, key, ef_kwargs[key])
                                ef_sample.save()
                                # now that we have a sample, it is time to deal with sweeps

                                # get a list of sweep times and figure out where to draw a line with respect to seconds vs. minutes
                                # sweeps_times = [s.sweep_time for s in models.Sweep.objects.all().order_by("sweep_time")]
                                # based on the histograms of sweep times, it seems like drawing the line at 100 would be reasonable
                                # but the decision of whether this operation should be applied, should only be assessed based on early sweeps (0, 0.5 and 1)
                                time_dict = {
                                    0: "SWEEP0_TIME",
                                    0.5: "SWEEP0_5_TIME",
                                    1: "SWEEP1_TIME",
                                    2: "SWEEP2_TIME",
                                    3: "SWEEP3_TIME",
                                    4: "SWEEP4_TIME",
                                    5: "SWEEP5_TIME",
                                    6: "SWEEP6_TIME",
                                }
                                sweep_keys = [time_dict[key] for key in time_dict]

                                # start out assuming time is recorded in seconds
                                time_in_minutes = False
                                for sweep_number in time_dict:
                                    sweep_key = time_dict[sweep_number]
                                    # first rule of the NoneObjects
                                    if r[sweep_key]:
                                        time = int(r[sweep_key])
                                        # next rule out any negative times
                                        if time > 0:
                                            notes = str()
                                            # do the test to see if we should convert to minutes
                                            if not time_in_minutes and (sweep_key in sweep_keys[:3]) and (time < 100):
                                                time_in_minutes = True
                                                notes = add_note(notes, "sweep time value from mastersheet multiplied by 60")
                                            # if this is sweep 0, there is a special note to be added and to set the program type as non-monitoring
                                            if sweep_key == sweep_keys[0]:
                                                notes = add_note(notes, "sweep number zero used as there is missing information about sampling protocol.")
                                                sample.monitoring_program = mp2
                                                sample.save()
                                            models.Sweep.objects.create(
                                                sample=sample,
                                                sweep_number=sweep_number,
                                                sweep_time=time if not time_in_minutes else time * 60,
                                                notes=notes if len(notes) else None,
                                            )
                    bar()


def make_histo():
    import pandas as pd
    import matplotlib.pyplot as plt
    from trapnet import models

    sweeps_times = [s.sweep_time for s in
                    models.Sweep.objects.filter(sweep_time__gte=0, sweep_time__lte=300).order_by("sweep_time")]
    df = pd.DataFrame({"sweep_times": sweeps_times})
    df.hist(bins=100)
    plt.show()


def get_life_stage_lookup():
    return {
        "151": 'am',
        "152": 'si',

        "1731": 'pa',
        "1732": 'sm',
        "1733": 'gr',
        "1734": 'sa',

        "1751": 'pa',
        "1752": 're',
        "1753": 'sr',

        "1781": 'pa',
        "1782": 're',
        "1783": 'sr',
    }


def run_process_fish():
    from alive_progress import alive_bar

    life_stage_lookup = get_life_stage_lookup()
    models.Specimen.objects.filter(old_id__istartswith="gd").delete()
    models.BiologicalDetailing.objects.filter(old_id__istartswith="gd").delete()

    with open(os.path.join(rootdir, 'problematic_fish_data.csv'), 'w') as wf:
        writer = csv.writer(wf, delimiter=',', lineterminator='\n')

        with open(os.path.join(rootdir, 'fish_data.csv'), 'r') as f:
            row_count = sum(1 for row in csv.reader(f)) - 1

        with open(os.path.join(rootdir, 'fish_data.csv'), 'r') as f:
            csv_reader = csv.DictReader(f)
            writer.writerow(list(csv_reader.fieldnames) + ["PROBLEM CODE", "DESCRIPTION OF PROBLEM", "GD_SAMPLE_ID", "WAS_IMPORTED"])
            with alive_bar(row_count, force_tty=True) as bar:  # declare your expected total
                for r in csv_reader:
                    # clean the row
                    for key in r:
                        r[key] = r[key].strip()  # remove any trailing spaces
                        if r[key] in ['', "NA"]:  # if there is a null value of any kind, replace with NoneObject
                            r[key] = None

                    file_type = r["FILE_TYPE"]
                    biological_sample = r["BIOLOGICAL_SAMPLE"]

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
                                writer.writerow([r[key] for key in r] + [1, f"There is no record of site '{r['SITE']}' in {sfa}", "", 0])
                            else:
                                writer.writerow([r[key] for key in r] + [2,
                                                                         f"There is no record of site '{r['SITE']}' in {sfa} being sampled on {start_date.strftime('%Y-%m-%d')}"])

                        elif qs.count() > 1:
                            writer.writerow([r[key] for key in r] + [3, "There is more than one site with same name being sampled on the same date!", "", 0])

                        else:
                            sample = qs.first()
                            # Now to deal with the sweep
                            sweep_number = r["SWEEP_NUMBER"]
                            if r["GD_ID"] == "138482":  # there was a simple omission error for this specimen. we number should be 0.5
                                sweep_number = 0.5
                            elif r["GD_ID"] in ["217374", "217375", "217394", "217446"]:  # there was a simple omission error for this specimen. we number should be 0.5
                                sweep_number = 3
                            if not sweep_number:
                                writer.writerow([r[key] for key in r] + [4, "This specimen has no sweep number", sample.old_id, 0])
                            else:
                                sweep_number = float(sweep_number)
                                sweeps = sample.sweeps.filter(sweep_number=sweep_number)
                                if not sweeps.exists():
                                    # here we need to add some complicated logic
                                    if sweep_number == 0 and sample.old_id == "GD_1857":
                                        sweep = models.Sweep.objects.create(sample=sample, sweep_number=0, sweep_time=0)
                                        sample.monitoring_program_id = 2
                                        sample.save()
                                    elif sweep_number == 0 and sample.old_id == "GD_1651":  # this should actually be in the sweep 0.5 category
                                        sweep = sample.sweeps.get(sweep_number=0.5)

                                    else:
                                        sweep = models.Sweep.objects.create(sample=sample, sweep_number=sweep_number, sweep_time=0)
                                        writer.writerow([r[key] for key in r] + [6, "no corresponding sweep time in the site data", sample.old_id, 1])
                                else:
                                    # cannot be more than one sweep per sample with the same number because of the unique_together constraint
                                    sweep = sweeps.first()

                                if sweep or file_type == "2" or biological_sample == "1":
                                    # get the species
                                    species = None
                                    try:
                                        species = models.Species.objects.get(tsn=r["SPECIES_ITIS_CODE"])
                                    except (models.Species.DoesNotExist, models.Species.MultipleObjectsReturned):

                                        # there are a few wierd ones
                                        notes = r["BIOLOGICAL_REMARKS"]
                                        if notes and "frog" in notes.lower():
                                            species = models.Species.objects.get(tsn=1094181)
                                        elif notes and "splake" in notes.lower():
                                            species = models.Species.objects.get(common_name_eng__icontains="splake")
                                        else:
                                            writer.writerow(
                                                [r[key] for key in r] + [7, f"Cannot find species with TSN {r['SPECIES_ITIS_CODE']} in db", sample.old_id, 0])

                                    if species:
                                        # life stage
                                        life_stage = life_stage_lookup.get(r['SPECIES_LIFE_STAGE'])
                                        if life_stage:
                                            life_stage = models.LifeStage.objects.get(code__iexact=life_stage)

                                        # status
                                        status = r['FISH_STATUS']
                                        if status:
                                            try:
                                                status = models.Status.objects.get(code__iexact=status)
                                            except:
                                                writer.writerow([r[key] for key in r] + [8, f"Cannot find status: {status}", sample.old_id, 1])
                                                status = None

                                        # adipose_condition
                                        origin = r['ORIGIN']
                                        adipose_condition = None
                                        if origin:
                                            if origin == "AC":
                                                adipose_condition = 0
                                            elif origin == "W":
                                                adipose_condition = 1

                                        # sex
                                        sex = r['SEX']
                                        if sex:
                                            sex = models.Sex.objects.get(code__iexact=sex)

                                        # maturity
                                        maturity = r['MATURITY']
                                        reproductive_status = None
                                        if maturity:
                                            maturity = models.Maturity.objects.get(code=int(maturity))
                                            if maturity.code == 4:
                                                reproductive_status = models.ReproductiveStatus.objects.get(code__iexact="p")

                                        age_type = r["AGE_TYPE"]
                                        if age_type:
                                            if age_type == "SCALE":
                                                age_type = 1
                                            elif age_type == "LGTHFREQ":
                                                age_type = 2
                                            else:
                                                writer.writerow([r[key] for key in r] + [9, f"Cannot find age type: {age_type}", sample.old_id, 1])
                                                age_type = None

                                        fish_kwargs = {
                                            "old_id": f'GD_{r["GD_ID"]}',
                                            "sweep": sweep,
                                            "species": species,
                                            "life_stage": life_stage,
                                            "status": status,
                                            "adipose_condition": adipose_condition,
                                            "fork_length": r["FORK_LENGTH"],
                                            "total_length": r["TOTAL_LENGTH"],
                                            "weight": r["WEIGHT"],
                                            "sex": sex,
                                            "maturity": maturity,
                                            "reproductive_status": reproductive_status,
                                            "age_type": age_type,
                                            "river_age": r["RIVER_AGE"],
                                            "scale_id_number": f'{r["SCALE_SAMPLE_ID"]} {sample.arrival_date.year}' if r["SCALE_SAMPLE_ID"] else None,
                                            "created_by_id": 50,
                                            "updated_by_id": 50,
                                        }
                                        notes = str()
                                        notes = add_note(notes, r["BIOLOGICAL_REMARKS"])
                                        if len(notes.strip()):
                                            fish_kwargs["notes"] = notes

                                        if file_type == "2" or biological_sample == "1":
                                            del fish_kwargs["sweep"]
                                            fish_kwargs["sample"] = sample
                                            models.BiologicalDetailing.objects.create(**fish_kwargs)
                                        else:
                                            catch_frequency = r["CATCH_FREQUENCY"]
                                            if catch_frequency and int(catch_frequency) > 0:
                                                for x in range(0, int(catch_frequency)):
                                                    models.Specimen.objects.create(**fish_kwargs)
                                            else:
                                                writer.writerow([r[key] for key in r] + [10, f"Catch frequency null or zero", sample.old_id, 0])
                    else:
                        writer.writerow([r[key] for key in r] + [0, "Fish specimen has no date/time", "", 0])
                    bar()


def process_master_files(process_samples=False, process_fish=False, qc_checks=False):
    if qc_checks:
        print("RUNNING INITIAL CHECKS")
        run_spp_checks()
        run_river_checks()

    if process_samples:
        print("PROCESSING SITE DATA")
        run_process_samples()

    if process_fish:
        print("PROCESSING FISH DATA")
        run_process_fish()





def run_process_fish_take2():
    """
    The first script did not correctly import the fish that were supposed to end up in the biological details table.
    """
    from alive_progress import alive_bar
    life_stage_lookup = get_life_stage_lookup()
    models.BiologicalDetailing.objects.filter(old_id__istartswith="gd").delete()

    with open(os.path.join(rootdir, 'problematic_fish_data_take2.csv'), 'w') as wf:
        writer = csv.writer(wf, delimiter=',', lineterminator='\n')

        with open(os.path.join(rootdir, 'fish_data.csv'), 'r') as f:
            row_count = sum(1 for row in csv.reader(f)) - 1

        with open(os.path.join(rootdir, 'fish_data.csv'), 'r') as f:
            csv_reader = csv.DictReader(f)
            writer.writerow(list(csv_reader.fieldnames) + ["PROBLEM CODE", "DESCRIPTION OF PROBLEM", "GD_SAMPLE_ID", "WAS_IMPORTED"])
            with alive_bar(row_count, force_tty=True) as bar:  # declare your expected total
                for r in csv_reader:
                    # clean the row
                    for key in r:
                        r[key] = r[key].strip()  # remove any trailing spaces
                        if r[key] in ['', "NA"]:  # if there is a null value of any kind, replace with NoneObject
                            r[key] = None

                    file_type = r["FILE_TYPE"]
                    biological_sample = r["BIOLOGICAL_SAMPLE"]
                    if file_type == "2" or biological_sample == "1":

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
                                    writer.writerow([r[key] for key in r] + [1, f"There is no record of site '{r['SITE']}' in {sfa}", "", 0])
                                else:
                                    writer.writerow([r[key] for key in r] + [2,
                                                                             f"There is no record of site '{r['SITE']}' in {sfa} being sampled on {start_date.strftime('%Y-%m-%d')}"])

                            elif qs.count() > 1:
                                writer.writerow([r[key] for key in r] + [3, "There is more than one site with same name being sampled on the same date!", "", 0])

                            else:
                                sample = qs.first()
                                # Now to deal with the sweep
                                sweep_number = r["SWEEP_NUMBER"]
                                if r["GD_ID"] == "138482":  # there was a simple omission error for this specimen. we number should be 0.5
                                    sweep_number = 0.5
                                elif r["GD_ID"] in ["217374", "217375", "217394", "217446"]:  # there was a simple omission error for this specimen. we number should be 0.5
                                    sweep_number = 3

                                if not sweep_number:
                                    writer.writerow([r[key] for key in r] + [4, "This specimen has no sweep number", sample.old_id, 0])
                                else:
                                    sweep_number = float(sweep_number)
                                    sweeps = sample.sweeps.filter(sweep_number=sweep_number)
                                    if not sweeps.exists():
                                        # here we need to add some complicated logic
                                        if sweep_number == 0 and sample.old_id == "GD_1857":
                                            sweep = models.Sweep.objects.create(sample=sample, sweep_number=0, sweep_time=0)
                                            sample.monitoring_program_id = 2
                                            sample.save()
                                        elif sweep_number == 0 and sample.old_id == "GD_1651":  # this should actually be in the sweep 0.5 category
                                            sweep = sample.sweeps.get(sweep_number=0.5)

                                        else:
                                            sweep = models.Sweep.objects.create(sample=sample, sweep_number=sweep_number, sweep_time=0)
                                            writer.writerow([r[key] for key in r] + [6, "no corresponding sweep time in the site data", sample.old_id, 1])
                                    else:
                                        # cannot be more than one sweep per sample with the same number because of the unique_together constraint
                                        sweep = sweeps.first()

                                    if sweep or file_type == "2" or biological_sample == "1":
                                        # get the species
                                        species = None
                                        try:
                                            species = models.Species.objects.get(tsn=r["SPECIES_ITIS_CODE"])
                                        except (models.Species.DoesNotExist, models.Species.MultipleObjectsReturned):

                                            # there are a few wierd ones
                                            notes = r["BIOLOGICAL_REMARKS"]
                                            if notes and "frog" in notes.lower():
                                                species = models.Species.objects.get(tsn=1094181)
                                            elif notes and "splake" in notes.lower():
                                                species = models.Species.objects.get(common_name_eng__icontains="splake")
                                            else:
                                                writer.writerow(
                                                    [r[key] for key in r] + [7, f"Cannot find species with TSN {r['SPECIES_ITIS_CODE']} in db", sample.old_id, 0])

                                        if species:
                                            # life stage
                                            life_stage = life_stage_lookup.get(r['SPECIES_LIFE_STAGE'])
                                            if life_stage:
                                                life_stage = models.LifeStage.objects.get(code__iexact=life_stage)

                                            # status
                                            status = r['FISH_STATUS']
                                            if status:
                                                try:
                                                    status = models.Status.objects.get(code__iexact=status)
                                                except:
                                                    writer.writerow([r[key] for key in r] + [8, f"Cannot find status: {status}", sample.old_id, 1])
                                                    status = None

                                            # adipose_condition
                                            origin = r['ORIGIN']
                                            adipose_condition = None
                                            if origin:
                                                if origin == "AC":
                                                    adipose_condition = 0
                                                elif origin == "W":
                                                    adipose_condition = 1

                                            # sex
                                            sex = r['SEX']
                                            if sex:
                                                sex = models.Sex.objects.get(code__iexact=sex)

                                            # maturity
                                            maturity = r['MATURITY']
                                            reproductive_status = None
                                            if maturity:
                                                maturity = models.Maturity.objects.get(code=int(maturity))
                                                if maturity.code == 4:
                                                    reproductive_status = models.ReproductiveStatus.objects.get(code__iexact="p")

                                            age_type = r["AGE_TYPE"]
                                            if age_type:
                                                if age_type == "SCALE":
                                                    age_type = 1
                                                elif age_type == "LGTHFREQ":
                                                    age_type = 2
                                                else:
                                                    writer.writerow([r[key] for key in r] + [9, f"Cannot find age type: {age_type}", sample.old_id, 1])
                                                    age_type = None

                                            fish_kwargs = {
                                                "old_id": f'GD_{r["GD_ID"]}',
                                                "sweep": sweep,
                                                "species": species,
                                                "life_stage": life_stage,
                                                "status": status,
                                                "adipose_condition": adipose_condition,
                                                "fork_length": r["FORK_LENGTH"],
                                                "total_length": r["TOTAL_LENGTH"],
                                                "weight": r["WEIGHT"],
                                                "sex": sex,
                                                "maturity": maturity,
                                                "reproductive_status": reproductive_status,
                                                "age_type": age_type,
                                                "river_age": r["RIVER_AGE"],
                                                "scale_id_number": f'{r["SCALE_SAMPLE_ID"]} {sample.arrival_date.year}' if r["SCALE_SAMPLE_ID"] else None,
                                                "created_by_id": 50,
                                                "updated_by_id": 50,
                                            }
                                            notes = str()
                                            notes = add_note(notes, r["BIOLOGICAL_REMARKS"])
                                            if len(notes.strip()):
                                                fish_kwargs["notes"] = notes

                                            # this is where my script was wrong the first time.
                                            # if file_type == "2" or biological_sample == "1":
                                            #     del fish_kwargs["sweep"]
                                            #     fish_kwargs["sample"] = sample
                                            #     models.BiologicalDetailing.objects.create(**fish_kwargs)
                                            # else:
                                            #     catch_frequency = r["CATCH_FREQUENCY"]
                                            #     if catch_frequency and int(catch_frequency) > 0:
                                            #         for x in range(0, int(catch_frequency)):
                                            #             models.Specimen.objects.create(**fish_kwargs)
                                            #     else:
                                            #         writer.writerow([r[key] for key in r] + [10, f"Catch frequency null or zero", sample.old_id, 0])
                        else:
                            writer.writerow([r[key] for key in r] + [0, "Fish specimen has no date/time", "", 0])
                    bar()