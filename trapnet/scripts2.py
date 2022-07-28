import csv
import datetime
import os

import pytz
from django.conf import settings
from django.db import IntegrityError
from django.utils.timezone import make_aware, now

from shared_models.utils import dotdict
from . import models

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
    with open(os.path.join(my_target_read_file), 'r', encoding='cp1252') as read_file:
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
                else:
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

def get_number_digits(mystr):
    if mystr:
        result = ""
        for char in mystr:
            if char.isdigit():
                result += char
        if len(result):
            return len(result)


def create_obs(kwargs):
    try:
        models.Observation.objects.create(**kwargs)
    except IntegrityError as e:
        print(e, kwargs)


def parse_row(row):
    status_code = row["Status"].lower() if row["Status"] else "r"
    status_id = models.Status.objects.get(code__iexact=status_code).id

    origin_code = row["Origin"]
    if origin_code:
        origin_code = "ha" if origin_code.lower() == "a" else origin_code
        origin_id = models.Origin.objects.get(code__iexact=origin_code).id
    else:
        origin_id = None

    sex = models.Sex.objects.get(code__iexact=row["Sex"]) if row["Sex"] else None
    sex_id = sex.id if sex else None

    removed_tags = row["tags removed"].strip() if row["tags removed"] else None
    removed_tags = [tag.strip() for tag in removed_tags.split(" ")] if removed_tags else []

    scale_id_number = row["Scale ID Number"].strip() if row["Scale ID Number"] else None
    if scale_id_number:
        scale_id_number += f' {row["Year"]}'
    freq = int(row["Freq"].strip()) if row["Freq"] else 1

    payload = {
        "freq": freq,
        "species_id": row["speciesId"],
        "life_stage_id": row["lifestageId"],
        "sample_id": row["sampleId"],
        "status_id": status_id,
        "origin_id": origin_id,
        "sex_id": sex_id,
        "fork_length": row["ForkLength"].strip() if row["ForkLength"] else None,
        "total_length": row["Total.Length"].strip() if row["Total.Length"] else None,
        "weight": row["Weight"].strip() if row["Weight"] else None,
        "river_age": row["Smolt.Age"].strip() if row["Smolt.Age"] else None,
        "first_tag": row["First.Tag"].strip() if row["First.Tag"] else None,
        "last_tag": row["Last.Tag"].strip() if row["Last.Tag"] else None,
        "scale_id_number": scale_id_number,
        "tags_removed": removed_tags,
        "notes": row["Comments"].strip() if row["Comments"] else None,
    }
    return dotdict(payload)


def import_smolt_data():
    # delete all observations from this datafile
    delete_rst_data()
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'trapnet', 'misc', 'master_smolt_data_DJF_June_2022_GD.csv')
    with open(os.path.join(my_target_data_file), 'r', encoding='cp1252') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        row_i = 1
        for row in my_csv:
            if row_i % 1000 == 0:
                print("starting row:", row_i)

            for key in row:
                row[key] = row[key].strip()
                if row[key].lower() in ["na", "n/a", ""]:
                    row[key] = None

            # only proceed is there is a species and sample
            new_row = parse_row(row)
            if new_row.species_id and new_row.sample_id:
                # this is a single observation
                kwargs = {
                    "sample_id": new_row.sample_id,
                    "species_id": new_row.species_id,
                    "life_stage_id": new_row.life_stage_id,
                    "status_id": new_row.status_id,
                    "origin_id": new_row.origin_id,
                    "sex_id": new_row.sex_id,
                    "fork_length": new_row.fork_length,
                    "total_length": new_row.total_length,
                    "weight": new_row.weight,
                    "river_age": new_row.river_age,
                    "scale_id_number": new_row.scale_id_number,
                    "notes": new_row.notes,
                    "tag_number": new_row.first_tag,
                    "created_at": now(),
                }
                if new_row.freq == 1:
                    create_obs(kwargs)
                else:
                    start_tag_prefix = get_prefix(new_row.first_tag)
                    start_tag = get_number_suffix(new_row.first_tag)
                    end_tag = get_number_suffix(new_row.last_tag)
                    padding = get_number_digits(new_row.first_tag)

                    if start_tag and end_tag:
                        diff = end_tag - start_tag
                        for i in range(0, diff + 1):
                            num = start_tag + i
                            num = str(num).rjust(padding, "0")
                            tag = f"{start_tag_prefix}{num}"
                            if tag in new_row.tags_removed:
                                print("not adding tag:", tag)
                            else:
                                kwargs["tag_number"] = tag
                                create_obs(kwargs)

                    elif start_tag and new_row.freq:
                        for i in range(0, new_row.freq):
                            num = start_tag + i
                            num = str(num).rjust(padding, "0")
                            tag = f"{start_tag_prefix}{num}"
                            if tag in new_row.tags_removed:
                                print("not adding tag:", tag)
                            else:
                                kwargs["tag_number"] = tag
                                create_obs(kwargs)

                    else:
                        kwargs["tag_number"] = None
                        for i in range(0, new_row.freq):
                            create_obs(kwargs)

            row_i += 1


def find_duplicate_scales():
    # get the unique list of scale ids
    observations = models.Observation.objects.filter(scale_id_number__isnull=False)
    scale_ids = set([o.scale_id_number for o in observations])

    for sid in scale_ids:
        if observations.filter(scale_id_number=sid).count() > 1:
            print(f"duplicate records found for: {sid}")


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
