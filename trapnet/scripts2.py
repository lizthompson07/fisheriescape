import csv
import datetime
import os
from random import randint

import pytz
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from django.utils.timezone import make_aware

from lib.templatetags.custom_filters import nz
from shared_models.models import River, FishingArea
from . import models

bad_codes = list()

site_conversion_dict = {
    "Butters": 334,
    "Kedgwick": 336,
    "LittleMain": 337,
    "Matapedia": 338,
    "Moses": 335,
    "Upsalquitch": 333,
}

species_conversion_dict = {
    "140": {"id": 1, "ls": None},
    "150": {"id": 2, "ls": None},
    "1320": {"id": 5, "ls": None},
    "1340": {"id": 6, "ls": None},
    "1490": {"id": 7, "ls": None},
    "1500": {"id": 8, "ls": None},
    "1509": {"id": 9, "ls": None},
    "1510": {"id": 10, "ls": None},
    "1520": {"id": 11, "ls": None},
    "1530": {"id": 12, "ls": None},
    "1550": {"id": 13, "ls": None},
    "1760": {"id": 26, "ls": None},
    "1770": {"id": 27, "ls": None},
    "1790": {"id": 31, "ls": None},
    "1800": {"id": 32, "ls": None},
    "1820": {"id": 33, "ls": None},
    "1880": {"id": 34, "ls": None},
    "1900": {"id": 35, "ls": None},
    "1910": {"id": 36, "ls": None},
    "2590": {"id": 37, "ls": None},
    "2600": {"id": 38, "ls": None},
    "2610": {"id": 39, "ls": None},
    "2620": {"id": 40, "ls": None},
    "2621": {"id": 41, "ls": None},
    "2630": {"id": 42, "ls": None},
    "2631": {"id": 43, "ls": None},
    "2640": {"id": 44, "ls": None},
    "2641": {"id": 45, "ls": None},
    "2642": {"id": 46, "ls": None},
    "2650": {"id": 47, "ls": None},
    "2651": {"id": 48, "ls": None},
    "2660": {"id": 49, "ls": None},
    "2670": {"id": 50, "ls": None},
    "2680": {"id": 51, "ls": None},
    "2690": {"id": 52, "ls": None},
    "2700": {"id": 53, "ls": None},
    "3410": {"id": 54, "ls": None},
    "4110": {"id": 55, "ls": None},
    "4120": {"id": 56, "ls": None},
    "4220": {"id": 57, "ls": None},
    "4230": {"id": 58, "ls": None},
    "4240": {"id": 59, "ls": None},
    "4260": {"id": 60, "ls": None},
    "4270": {"id": 61, "ls": None},
    "4280": {"id": 62, "ls": None},
    "4420": {"id": 63, "ls": None},
    "4640": {"id": 64, "ls": None},
    "5390": {"id": 65, "ls": None},
    "5720": {"id": 66, "ls": None},
    "5930": {"id": 67, "ls": None},
    "5940": {"id": 68, "ls": None},
    "5950": {"id": 69, "ls": None},
    "8080": {"id": 70, "ls": None},
    "8250": {"id": 71, "ls": None},
    "8260": {"id": 72, "ls": None},
    "8870": {"id": 73, "ls": None},
    "8940": {"id": 74, "ls": None},
    "8950": {"id": 75, "ls": None},
    "9001": {"id": 77, "ls": None},
    "9002": {"id": 78, "ls": None},
    "9070": {"id": 76, "ls": None},

    "151": {"id": 2, "ls": 13},
    "152": {"id": 2, "ls": 14},

    "1731": {"id": 79, "ls": 1},
    "1732": {"id": 79, "ls": 2},
    "1734": {"id": 79, "ls": 4},

    "1751": {"id": 24, "ls": 1},
    "1752": {"id": 24, "ls": 7},

    "1781": {"id": 80, "ls": 1},
    "1782": {"id": 80, "ls": 7},
    "1783": {"id": 80, "ls": 8},
}


def delete_rst_data():
    observations = models.Observation.objects.filter(sample__sample_type=1, sample__season__lte=2021)
    observations.delete()


def convert_river_to_site(river):
    return site_conversion_dict.get(river)


def convert_sp_code_to_id(code):
    d1 = species_conversion_dict.get(code)

    if not d1:
        print(f'cannot find code "{code}" in species dict')
    else:
        id = d1["id"]
        ls = d1["ls"]
        payload = dict(
            species=id,
            life_stage=ls,
        )
        return payload


def get_deep_sample(row_dict):
    raw_arrival_time = row_dict["Time.Start"]
    if raw_arrival_time and ":" in raw_arrival_time:
        hour = raw_arrival_time.split(":")[0]
        min = raw_arrival_time.split(":")[1]
    else:
        hour = "12"
        min = "00"
    arrival_dt_string = f'{row_dict["Year"]}-{row_dict["Month"]}-{row_dict["Day"]} {hour}:{min}'
    arrival_date = make_aware(datetime.datetime.strptime(arrival_dt_string, "%Y-%m-%d %H:%M"), timezone=pytz.timezone("Canada/Atlantic"))
    try:
        sample = models.Sample.objects.get(
            site=row_dict["siteId"],
            arrival_date=arrival_date,
        )
        return sample
    except Exception as e:
        print("cannot find sample:", e, row_dict)


def get_sample(row_dict):
    try:
        sample = models.Sample.objects.get(
            site_id=row_dict["siteId"],
            arrival_date__year=row_dict["Year"],
            arrival_date__month=row_dict["Month"],
            arrival_date__day=row_dict["Day"],
        )
    except Exception as e:
        print("attempting deep dive:", e)
        sample = get_deep_sample(row_dict)
    return sample


def write_samples_to_table():
    my_target_read_file = os.path.join(settings.BASE_DIR, 'trapnet', 'misc', 'master_smolt_data_GD_Jun_2022.csv')
    my_target_write_file = os.path.join(settings.BASE_DIR, 'trapnet', 'misc', 'master_smolt_data_DJF_June_2022.csv')
    with open(os.path.join(my_target_read_file), 'r') as read_file:
        reader = csv.reader(read_file)
        with open(os.path.join(my_target_write_file), 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            i = 0
            header_row = list()
            for row in reader:
                row_dict = dict()
                if i == 0:
                    writer.writerow(row)
                    header_row = row
                elif i < 100:
                    # get the row_dict
                    col_count = 0
                    for col in row:
                        row_dict[header_row[col_count]] = col
                        col_count += 1

                    # GET SITE
                    row_dict["siteId"] = convert_river_to_site(row_dict["River"])
                    row[1] = row_dict["siteId"]

                    # GET SAMPLES
                    if not row_dict["sampleId"]:
                        sample = get_sample(row_dict)
                        # sample = None
                        # if there is a sample, we update the row
                        if sample:
                            row[7] = sample.id

                    # GET SPECIES
                    code = row_dict["Species"]
                    mydict = convert_sp_code_to_id(code)
                    if mydict:
                        species = mydict["species"]
                        life_stage = mydict.get("life_stage")
                        if species:
                            row[8] = species
                        if life_stage:
                            row[9] = life_stage
                    writer.writerow(row)

                # display progress
                if i % 1000 == 0:
                    print(i)

                # right the updated row to file
                i += 1


def get_prefix(mystr):
    if mystr:
        result = ""
        for char in mystr:
            if not char.isdigit():
                result += char
        if len(result):
            return result


def get_number_suffix(mystr):
    if mystr:
        result = ""
        for char in mystr:
            if char.isdigit():
                result += char
        if len(result):
            return int(result)


def check_entries_2_obs():
    for entry in models.Entry.objects.filter(
            first_tag__isnull=False,
            last_tag__isnull=True,
            frequency__isnull=False
    ):
        if entry.frequency > 1:
            print(entry.first_tag, entry.frequency)


def create_obs(kwargs):
    try:
        models.Observation.objects.create(**kwargs)
    except IntegrityError:
        print("dealing with dup")
        old_tag = kwargs.get("tag_number")
        print("Duplicate tag number!! ", old_tag)
        new_tag = f'{old_tag}.{randint(1, 1000)}'
        kwargs["tag_number"] = new_tag
        print("Duplicate tag number!! ", old_tag, " to ", new_tag)
        models.Observation.objects.create(**kwargs)


def entries_2_obs():
    # remove all previous observations from rst
    models.Observation.objects.filter(sample__sample_type=1).delete()
    now = timezone.now()
    j = 1
    for entry in models.Entry.objects.all():
        if j % 1000 == 0:
            print("starting row", j)
        if entry.species:
            kwargs = {
                "sample": entry.sample,
                "species": entry.species,
                "status": entry.status,
                "origin": entry.origin,
                "sex": entry.sex,
                "fork_length": entry.fork_length,
                "total_length": entry.total_length,
                "weight": entry.weight,
                "tag_number": entry.first_tag,
                "scale_id_number": entry.scale_id_number,
                "tags_removed": entry.tags_removed,
                "notes": entry.notes,
                "created_at": now,
            }

            # determine if this is a single observation
            if not entry.last_tag and (entry.frequency == 1 or entry.frequency is None):
                # this means we are dealing with a single observation
                create_obs(kwargs)
            else:
                start_tag_prefix = get_prefix(entry.first_tag)
                start_tag = get_number_suffix(entry.first_tag)
                end_tag = get_number_suffix(entry.last_tag)

                if start_tag and end_tag:
                    diff = end_tag - start_tag
                    for i in range(0, diff):
                        tag = f"{start_tag_prefix}{start_tag + i}"
                        kwargs["tag_number"] = tag
                        create_obs(kwargs)
                elif start_tag and entry.frequency:
                    for i in range(0, entry.frequency):
                        tag = f"{start_tag_prefix}{start_tag + i}"
                        kwargs["tag_number"] = tag
                        create_obs(kwargs)
                elif entry.frequency:
                    for i in range(0, entry.frequency):
                        create_obs(kwargs)
                else:
                    create_obs(kwargs)
        j += 1


def comment_samples_from_matapedia():
    for sample in models.Sample.objects.filter(site_id=338):
        if sample.notes:
            sample.notes += "; Data collected and owned by the Gespe'gewaq Mi'gmaq Resource Council (GMRC)."
        else:
            sample.notes = "Data collected and owned by the Gespe'gewaq Mi'gmaq Resource Council (GMRC)."
        sample.save()


def add_comment(comment, addition):
    if addition and addition != "":
        if not comment or comment == "":
            comment = addition
        else:
            comment += f"; {addition}"
    return comment


def is_number_tryexcept(s):
    """ Returns True is string is a number. https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float """
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def import_smolt_data():
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'trapnet', 'misc', 'master_smolt_data_GD_Jul_2021.csv')
    with open(os.path.join(my_target_data_file), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        i = 1
        for row in my_csv:
            if i % 1000 == 0:
                print("starting row", i)
            for key in row:
                if row[key].lower().strip() in ["na", "n/a", ""]:
                    row[key] = None

            comment = ""
            site = models.RiverSite.objects.get(pk=row["River"])

            # deal with arrival and departure dts
            raw_arrival_time = row["Time.Start"]

            if raw_arrival_time and "&" in raw_arrival_time:
                raw_arrival_time = raw_arrival_time.split("&")[0].strip()
            if raw_arrival_time and ":" in raw_arrival_time:
                hour = raw_arrival_time.split(":")[0]
                min = raw_arrival_time.split(":")[1]
            else:
                hour = "12"
                min = "00"
                comment = add_comment(comment, "Import data did not contain arrival time")
            arrival_dt_string = f'{row["Year"]}-{row["Month"]}-{row["Day"]} {hour}:{min}'
            arrival_date = make_aware(datetime.datetime.strptime(arrival_dt_string, "%Y-%m-%d %H:%M"), timezone=pytz.timezone("Canada/Atlantic"))

            # check to see if there is a direct hit using only year, month, day
            samples = models.Sample.objects.filter(
                site=site,
                sample_type=1,
                arrival_date__year=arrival_date.year,
                arrival_date__month=arrival_date.month,
                arrival_date__day=arrival_date.day,
            )

            if samples.count() == 0:
                print("big problem for obs id={}. no sample found for site={}, date={}/{}/{}".format(
                    row["id"],
                    site,
                    row["Year"],
                    row["Month"],
                    row["Day"],
                ))

            elif samples.count() > 1:
                print("small problem for obs id={}. multiple samples found for site={}, date={}/{}/{}".format(
                    row["id"],
                    site,
                    row["Year"],
                    row["Month"],
                    row["Day"],
                ))
                for s in samples:
                    print(s.arrival_date, row["Time.Start"])
                print("going to put all observations in the first sample")
            if samples.exists():
                # there has been  1 or more hits and we can create the observation in the db
                my_obs, created = models.Entry.objects.get_or_create(
                    id=int(row["id"]),
                )
                if created:
                    # if there is either a date or location tagged, we will put this in the notes. We discussed this with guillaume to drop this field
                    location_tagged = nz(row["Location.Tagged"].strip(), None) if row["Location.Tagged"] else None
                    if location_tagged:
                        add_comment(comment, f"location tagged: {location_tagged}")

                    date_tagged = nz(row["Date.Tagged"].strip(), None) if row["Date.Tagged"] else None
                    if date_tagged:
                        add_comment(comment, f"date tagged: {date_tagged}")

                    try:
                        species = models.Species.objects.get(code__iexact=row["Species"]) if row["Species"] else None
                        status = models.Status.objects.get(code__iexact=row["Status"]) if row["Status"] else None
                        origin = models.Origin.objects.get(code__iexact=row["Origin"]) if row["Origin"] else None
                        sex = models.Sex.objects.get(code__iexact=row["Sex"]) if row["Sex"] else None
                    except Exception as E:
                        print(E)
                        print(
                            f'Species={row["Species"]} Status={row["Status"]} '
                            f'Origin={row["Origin"]} Sex={row["Sex"]}'
                        )
                    my_obs.species = species
                    my_obs.sample = samples.first()
                    my_obs.first_tag = row["First.Tag"].strip() if row["First.Tag"] else None
                    my_obs.last_tag = row["Last.Tag"].strip() if row["Last.Tag"] else None
                    my_obs.status = status
                    my_obs.origin = origin
                    my_obs.frequency = row["Freq"].strip() if row["Freq"] else None
                    my_obs.fork_length = row["ForkLength"].strip() if row["ForkLength"] else None
                    my_obs.total_length = row["Total.Length"].strip() if row["Total.Length"] else None
                    my_obs.weight = row["Weight"].strip() if row["Weight"] else None
                    my_obs.sex = sex
                    my_obs.smolt_age = row["Smolt.Age"].strip() if row["Smolt.Age"] else None
                    my_obs.scale_id_number = row["Scale ID Number"].strip() if row["Scale ID Number"] else None
                    my_obs.tags_removed = row["tags removed"].strip() if row["tags removed"] else None
                    my_obs.notes = row["Comments"].strip() if row["Comments"] else None

                    try:
                        my_obs.save()
                    except Exception as e:
                        print(e)
                        print(my_obs.id)

            i += 1


def transfer_life_stage():
    for obs in models.Observation.objects.filter(species__life_stage__isnull=False):
        obs.life_stage_id = obs.species.life_stage_id
        obs.save()


def clean_up_lamprey():
    s150 = models.Species.objects.get(code=150)  # good one
    s151 = models.Species.objects.get(code=151)  # ammocoete
    s152 = models.Species.objects.get(code=152)  # silver
    life_stage_ammocoete, created = models.LifeStage.objects.get_or_create(name="ammocoete")
    life_stage_silver, created = models.LifeStage.objects.get_or_create(name="silver")

    for obs in s151.observations.all():
        obs.species_id = s150.id
        obs.life_stage_id = life_stage_ammocoete.id
        obs.save()

    for obs in s152.observations.all():
        obs.species_id = s150.id
        obs.life_stage_id = life_stage_silver.id
        obs.save()

    s151.delete()
    s152.delete()


def create_river_areas():
    for r in River.objects.all():
        if r.fishing_area_code:
            fa, created = FishingArea.objects.get_or_create(name=r.fishing_area_code.upper())
            r.fishing_area = fa
            r.save()


def find_duplicate_scales():
    # get the unique list of scale ids
    observations = models.Observation.objects.filter(scale_id_number__isnull=False)
    scale_ids = set([o.scale_id_number for o in observations])

    for sid in scale_ids:
        if observations.filter(scale_id_number=sid).count() > 1:
            print(f"duplicate records found for: {sid}")


def annotate_scales():
    # get the unique list of scale ids
    observations = models.Observation.objects.filter(scale_id_number__isnull=False)

    for o in observations:
        o.scale_id_number += f" {o.sample.season}"
        o.save()

    find_duplicate_scales()


def populate_len():
    fl_observations = models.Observation.objects.filter(fork_length__isnull=False, length__isnull=True)
    for o in fl_observations:
        o.length = o.fork_length
        o.length_type = 1
        o.save()

    tot_observations = models.Observation.objects.filter(total_length__isnull=False, length__isnull=True)
    for o in tot_observations:
        o.length = o.total_length
        o.length_type = 2
        o.save()


def delete_tags_removed():
    observations = models.Observation.objects.filter(tags_removed__isnull=False, tag_number__isnull=False)
    for obs in observations:

        # get a list of tags from the removed_tags
        removed_tags = obs.tags_removed.split(" ")
        # trim away any whitespace
        removed_tags = [tag.strip() for tag in removed_tags]
        # determine the number of digits in the tag. all the tags should have the same number of digits
        tag_lens = len(set([len(tag) for tag in removed_tags]))
        # the tag_lens list should only have a length of one. otherwise that means there is inconsistent lengths and that we have a problem
        if tag_lens > 1:
            print("cannot process these tags:", removed_tags)
        else:
            # we are good to proceed
            digits = len(removed_tags[0])
            # if the observation tag number is not the same length as the reference tag number, we'll have to do some surgery
            if not digits == len(obs.tag_number):
                # print(obs.tag_number, "does not conform to the format of tags removed:", removed_tags)
                pos = len(obs.tag_number) - 1
                new_tag = f"{obs.tag_number[0]}0{obs.tag_number[-pos:]}"
                if not digits == len(new_tag):
                    # try adding another zero
                    pos = len(new_tag) - 1
                    new_tag = f"{new_tag[0]}0{new_tag[-pos:]}"
                    if not digits == len(new_tag):
                        # try adding another zero
                        pos = len(new_tag) - 1
                        new_tag = f"{new_tag[0]}0{new_tag[-pos:]}"
                        if not digits == len(new_tag):
                            print("still bad:", new_tag, "compared to:", removed_tags)

                if not new_tag[1] == removed_tags[0][1]:
                    # print("still bad:", new_tag, "first char is different:", removed_tags)
                    pass
                else:
                    obs.tag_number = new_tag
                    obs.save()

            if obs.tag_number in removed_tags:
                print("This observation is being deleted:", obs.tag_number, removed_tags)
                obs.delete()


def import_smolt_ages():
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'trapnet', 'misc', 'smolt_ages_to_import.csv')
    with open(os.path.join(my_target_data_file), 'r') as csv_read_file:

        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            scale_id = row["Scale ID Number"].strip()
            qs = models.Observation.objects.filter(scale_id_number=scale_id)
            if not qs.exists():
                scale_id = scale_id + f' {row["Year"]}'
                qs = models.Observation.objects.filter(scale_id_number=scale_id)
                if not qs.exists():
                    print("cannot find scale number:", scale_id)
                elif qs.count() > 1:
                    print("too many results:", scale_id)
                else:
                    # print(f"ready to insert age for scale_id {scale_id}: {row['Smolt.Age']}")
                    obs = qs.first()
                    obs.river_age = row['Smolt.Age']
                    obs.save()
            else:
                # let's deal with the ones with multiple frequencies
                freq = int(row["Freq"])
                raw_arrival_time = row["Time.Start"]
                raw_departure_time = row["Time.Released"]
                if raw_arrival_time and ":" in raw_arrival_time:
                    hour = raw_arrival_time.split(":")[0]
                    min = raw_arrival_time.split(":")[1]
                else:
                    hour = "12"
                    min = "00"
                    comment = add_comment(comment, "Import data did not contain arrival time")
                arrival_dt_string = f'{row["Year"]}-{row["Month"]}-{row["Day"]} {hour}:{min}'
                if raw_departure_time and ":" in raw_departure_time:
                    hour = raw_departure_time.split(":")[0]
                    min = raw_departure_time.split(":")[1]
                else:
                    hour = "12"
                    min = "00"
                departure_dt_string = f'{row["Year"]}-{row["Month"]}-{row["Day"]} {hour}:{min}'
                arrival_date = make_aware(datetime.datetime.strptime(arrival_dt_string, "%Y-%m-%d %H:%M"), timezone=pytz.timezone("Canada/Atlantic"))
                departure_date = make_aware(datetime.datetime.strptime(departure_dt_string, "%Y-%m-%d %H:%M"), timezone=pytz.timezone("Canada/Atlantic"))
                site = models.RiverSite.objects.get(pk=row["River"])

                if freq > 1:
                    # find out how many exist from that date
                    qs = models.Observation.objects.filter(
                        sample__site=site,
                        sample__arrival_date=arrival_date,
                        tag_number__isnull=True,
                        status__code__iexact="r",
                        river_age__isnull=True,
                        length=None,
                    )
                    print(qs.count(), freq, qs.count() > freq)
                    i = 1
                    for obs in qs:
                        obs.river_age = row['Smolt.Age']
                        obs.save()
                        print("updating:", i, obs.id)
                        qs0 = models.Observation.objects.filter(
                            sample__site=site,
                            sample__arrival_date=arrival_date,
                            tag_number__isnull=True,
                            status__code__iexact="r",
                            river_age=row['Smolt.Age'],
                            length=None,
                        )
                        if qs0.count() == freq:
                            break
                        i += 1
                else:
                    species = int(row["species"])
                    life_stage_id = row["life_stage_id"]
                    if species == 79 and life_stage_id == "1":
                        qs = models.Observation.objects.filter(
                            sample__site=site,
                            sample__arrival_date=arrival_date,
                            tag_number__isnull=True,
                            status__code__iexact="r",
                            river_age__isnull=True,
                            notes__icontains=row["Comments"],
                        )
                        if qs.count() == 1:
                            obs = qs.first()
                            obs.river_age = row['Smolt.Age']
                            obs.save()
                    if species == 79 and life_stage_id == "2":
                        qs = models.Observation.objects.filter(
                            sample__site=site,
                            sample__arrival_date=arrival_date,
                            tag_number__isnull=True,
                            status__code__iexact=row["Status"],
                            river_age__isnull=True,
                            # notes__icontains=row["Comments"],
                            fork_length=row["ForkLength"]
                        )
                        if qs.count() == 1:
                            obs = qs.first()
                            obs.river_age = row['Smolt.Age']
                            obs.save()

                    if species == 24:
                        qs = models.Observation.objects.filter(
                            sample__site=site,
                            sample__arrival_date=arrival_date,
                            tag_number__isnull=True,
                            status__code__iexact=row["Status"],
                            river_age__isnull=True,
                            fork_length=row["ForkLength"]
                        )
                        print(qs.count())
                        if qs.count() == 1:
                            obs = qs.first()
                            obs.river_age = row['Smolt.Age']
                            obs.save()
                    elif species == 54:
                        qs = models.Observation.objects.filter(
                            sample__site=site,
                            sample__arrival_date=arrival_date,
                            tag_number__isnull=True,
                            status__code__iexact=row["Status"],
                            river_age__isnull=True,
                            total_length=row["Total.Length"],
                            weight=row["Weight"],
                            notes__icontains=row["Comments"],
                        )
                        if qs.count() == 1:
                            obs = qs.first()
                            obs.river_age = row['Smolt.Age']
                            obs.save()
