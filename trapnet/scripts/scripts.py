import csv
import datetime
import os
from random import randint

import pytz
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count
from django.utils import timezone
from django.utils.timezone import make_aware

from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from shared_models.models import River, FishingArea
from .. import models


def delete_rst_data():
    models.Specimen.objects.filter(sample__sample_type=1).delete()
    models.Entry.objects.all().delete()
    models.Sweep.objects.filter(sample__sample_type=1).delete()
    models.Sample.objects.filter(sample_type=1).delete()


def delete_rst_entries():
    models.Entry.objects.all().delete()


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


def check_entries_2_specimen():
    for entry in models.Entry.objects.filter(
            first_tag__isnull=False,
            last_tag__isnull=True,
            frequency__isnull=False
    ):
        if entry.frequency > 1:
            print(entry.first_tag, entry.frequency)


def create_specimen(kwargs):
    try:
        models.Specimen.objects.create(**kwargs)
    except IntegrityError:
        print("dealing with dup")
        old_tag = kwargs.get("tag_number")
        print("Duplicate tag number!! ", old_tag)
        new_tag = f'{old_tag}.{randint(1, 1000)}'
        kwargs["tag_number"] = new_tag
        print("Duplicate tag number!! ", old_tag, " to ", new_tag)
        models.Specimen.objects.create(**kwargs)


def entries_2_specimen():
    # remove all previous specimens from rst
    models.Specimen.objects.filter(sample__sample_type=1).delete()
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

            # determine if this is a single specimen
            if not entry.last_tag and (entry.frequency == 1 or entry.frequency is None):
                # this means we are dealing with a single specimen
                create_specimen(kwargs)
            else:
                start_tag_prefix = get_prefix(entry.first_tag)
                start_tag = get_number_suffix(entry.first_tag)
                end_tag = get_number_suffix(entry.last_tag)

                if start_tag and end_tag:
                    diff = end_tag - start_tag
                    for i in range(0, diff):
                        tag = f"{start_tag_prefix}{start_tag + i}"
                        kwargs["tag_number"] = tag
                        create_specimen(kwargs)
                elif start_tag and entry.frequency:
                    for i in range(0, entry.frequency):
                        tag = f"{start_tag_prefix}{start_tag + i}"
                        kwargs["tag_number"] = tag
                        create_specimen(kwargs)
                elif entry.frequency:
                    for i in range(0, entry.frequency):
                        create_specimen(kwargs)
                else:
                    create_specimen(kwargs)
        j += 1


def population_parents():
    for river in shared_models.River.objects.all():
        if river.parent_cgndb_id:
            # get the river, if it exists
            try:
                parent_river = shared_models.River.objects.get(cgndb=river.parent_cgndb_id)
            except shared_models.River.DoesNotExist:
                pass
            else:
                river.parent_river = parent_river
                river.save()


def resave_traps():
    for trap in models.Sample.objects.filter(season__isnull=True):
        trap.save()


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


wind_dict = {
    "calm".lower(): dict(speed=2, direction=None),
    "Calm".lower(): dict(speed=2, direction=None),
    "calm(increasing)".lower(): dict(speed=2, direction=None),
    "calme".lower(): dict(speed=2, direction=None),
    "heavy".lower(): dict(speed=5, direction=None),
    "light".lower(): dict(speed=3, direction=None),
    "medium".lower(): dict(speed=4, direction=None),
    "moderate".lower(): dict(speed=4, direction=None),
    "NA".lower(): dict(speed=1, direction=None),
    "No wind".lower(): dict(speed=1, direction=None),
    "no wind".lower(): dict(speed=1, direction=None),
    "none".lower(): dict(speed=1, direction=None),
    "slight".lower(): dict(speed=2, direction=None),
    "slight(increasing)".lower(): dict(speed=2, direction=None),
    "strong".lower(): dict(speed=5, direction=None),
    "Varible wind gusts".lower(): dict(speed=6, direction=None),
    "Windy".lower(): dict(speed=4, direction=None),
    "windy".lower(): dict(speed=4, direction=None),
    "little wind".lower(): dict(speed=2, direction=None),
    "strong north".lower(): dict(speed=5, direction=1),
    "light north".lower(): dict(speed=3, direction=1),
    "light northerly".lower(): dict(speed=3, direction=1),
    "moderate NE".lower(): dict(speed=4, direction=2),
    "Moderate North East".lower(): dict(speed=4, direction=2),
    "light NE".lower(): dict(speed=3, direction=2),
    "slight NE".lower(): dict(speed=2, direction=2),
    "strong NE".lower(): dict(speed=5, direction=2),
    "strong north east".lower(): dict(speed=5, direction=2),
    "brisk east".lower(): dict(speed=3, direction=3),
    "Light E".lower(): dict(speed=3, direction=3),
    "Light East".lower(): dict(speed=3, direction=3),
    "med east".lower(): dict(speed=4, direction=3),
    "medeast".lower(): dict(speed=4, direction=3),
    "mod east".lower(): dict(speed=4, direction=3),
    "Mod east".lower(): dict(speed=4, direction=3),
    "moderate east".lower(): dict(speed=4, direction=3),
    "moderate easterly".lower(): dict(speed=4, direction=3),
    "slight east".lower(): dict(speed=2, direction=3),
    "slight east ".lower(): dict(speed=2, direction=3),
    "stong east".lower(): dict(speed=5, direction=3),
    "strong east".lower(): dict(speed=5, direction=3),
    "Brisk SE".lower(): dict(speed=3, direction=4),
    "Light SE".lower(): dict(speed=3, direction=4),
    "slight SE".lower(): dict(speed=2, direction=4),
    "Light South".lower(): dict(speed=3, direction=5),
    "light southerly".lower(): dict(speed=3, direction=5),
    "moderate south".lower(): dict(speed=4, direction=5),
    "Brisk SW".lower(): dict(speed=3, direction=6),
    "Light SW".lower(): dict(speed=3, direction=6),
    "Slight SW".lower(): dict(speed=2, direction=6),
    "Brisk West".lower(): dict(speed=3, direction=7),
    "Light W".lower(): dict(speed=3, direction=7),
    "Light West".lower(): dict(speed=3, direction=7),
    "light westerly".lower(): dict(speed=3, direction=7),
    "med west".lower(): dict(speed=4, direction=7),
    "medwest".lower(): dict(speed=4, direction=7),
    "mod ouest".lower(): dict(speed=4, direction=7),
    "mod west".lower(): dict(speed=4, direction=7),
    "moderate northerly".lower(): dict(speed=4, direction=7),
    "Moderate West".lower(): dict(speed=4, direction=7),
    "slight west".lower(): dict(speed=2, direction=7),
    "strong west".lower(): dict(speed=5, direction=7),
    "strong west ".lower(): dict(speed=5, direction=7),
    "light ouest".lower(): dict(speed=3, direction=7),
    "Brisk NW".lower(): dict(speed=3, direction=8),
    "calm(increasing NW)".lower(): dict(speed=2, direction=8),
    "Calm/Light NW".lower(): dict(speed=2, direction=8),
    "Light/strong NW".lower(): dict(speed=3, direction=8),
    "moderate NW".lower(): dict(speed=4, direction=8),
    "slight  NW".lower(): dict(speed=2, direction=8),
    "slight NW".lower(): dict(speed=2, direction=8),
    "Strong NW".lower(): dict(speed=5, direction=8),
    "Light NW".lower(): dict(speed=3, direction=8),
    "moderate n,w".lower(): dict(speed=4, direction=8),
    "".lower(): dict(speed=None, direction=None),
}
operating_condition_dict = {
    "70% operating": 2,
    "bad": 2,
    "cleaner jam": 2,
    "cleaner jammed": 2,
    "cleaner jammed; water overflowing holding box": 2,
    "cleaner not working": 2,
    "fully": 1,
    "fully after re-launch": 1,
    "fully operation": 1,
    "fully operation ivan,kevin,": 1,
    "fully operational": 1,
    "fully operational, minimal debris in box": 1,
    "fully operational, moved wheel into shore to catch more current and increase rpms": 1,
    "fully operational, one branch in drum": 1,
    "fully operational, some debris in box": 1,
    "fully operational, very little debris in box": 1,
    "fully operational,some debris in box": 1,
    "fully operaton": 1,
    "fully*": 1,
    "good": 1,
    "good - tire is not turning": 1,
    "good - tire is not turning - branch is still there": 1,
    "good - tire is not turning, branch is gone": 1,
    "good - tire is not turning, there's a big branch that dusty took off and another branch stucked on the shaft but is doesn't seem to slow down the wheel": 1,
    "good - wheel is slower than normal but nothing seems to block it": 1,
    "good - wheel rpm is back to normal": 1,
    "jam removed": 1,
    "jammed": 2,
    "jammed/not set": 3,
    "na": None,
    "no cleaner": 2,
    "not": None,
    "not 100%": 2,
    "not functioning": 3,
    "not operating": 3,
    "not operating, wheel jammed with 4 foot log": 3,
    "not operating, wheel jammed with a 30 foot log": 3,
    "not set": 3,
    "operating fully": 1,
    "operating fully (little debris)": 1,
    "operating fully (little small debris)": 1,
    "operating fully (lots of small debris)": 1,
    "operating fully (moved wheel out 1 section)": 1,
    "operating fully (very little debris)": 1,
    "operating fully (very little fine debris)": 1,
    "operating fully(drum dirty)": 1,
    "operating fully,": 1,
    "operating fully, cleaned drum": 1,
    "operating fully, cleaner fixed and working good": 1,
    "operating fully, little debris in box": 1,
    "operating fully, little debris in box cleaned drum": 1,
    "operating fully, little debris in box drum cleaned": 1,
    "operating fully, little debris in box,": 1,
    "operating fully, little debris in box, cleaned drum with brush to increase rpms and reduce current in box": 1,
    "operating fully, little debris in box, larger stick in drum": 1,
    "slow, a big long branch is stuck in it": 2,
    "small tree in wheel, still functioning": 2,
    "smolt wheel was found closer to shore in less current and the lock was missing. reported to rcmp and dfo c&p. wheel reset to original position.": 3,
    "tire don't turn": 2,
    "trap set": 1,
    "we took out the branch": 1,
    "wheel is touching the bottom of the river, it's very slow": 2,
    "wheel jammed with an 8 foot piece of pulp": 2,
    "wheel not set last evening": 3,
    "wheel rotating good but holding box blocked with fine debris, cleaner not working": 2,
    "wheel turning but cleaner not working": 2,
    "wheel up": 3,
    "": None,
}


def is_number_tryexcept(s):
    """ Returns True is string is a number. https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float """
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def import_trap_data():
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'trapnet', 'misc', 'smolts_trapdata_master.csv')
    with open(os.path.join(my_target_data_file), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            for key in row:
                if row[key].lower() in ["na", "n/a", ""]:
                    row[key] = None

            comment = ""
            site = models.RiverSite.objects.get(pk=row["River"])

            # deal with arrival and departure dts
            raw_arrival_time = row["Time_arrival"]
            raw_departure_time = row["Time_departure"]

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
                comment = add_comment(comment, "Import data did not contain departure time")
            departure_dt_string = f'{row["Year"]}-{row["Month"]}-{row["Day"]} {hour}:{min}'
            arrival_date = make_aware(datetime.datetime.strptime(arrival_dt_string, "%Y-%m-%d %H:%M"), timezone=pytz.timezone("Canada/Atlantic"))
            departure_date = make_aware(datetime.datetime.strptime(departure_dt_string, "%Y-%m-%d %H:%M"), timezone=pytz.timezone("Canada/Atlantic"))
            sample, created = models.Sample.objects.get_or_create(
                site=site,
                sample_type=1,
                arrival_date=arrival_date,
                departure_date=departure_date,
            )

            comment = add_comment(comment, row["Comments"])
            cloud = None
            if row["Cloud_cover_pcent "]:
                cloud = nz(row["Cloud_cover_pcent "].strip().lower().replace("%", ""), None)
                if cloud and cloud != "0":
                    if is_number_tryexcept(cloud):
                        cloud = int(cloud) / 100
                    elif "no cloud" in cloud or "na" in cloud:
                        cloud = 0
                    elif "cloudy" in cloud:
                        cloud = 0.5

            # now that we have a sample, we can deal with the rest of the fields
            sample.air_temp_arrival = row["Airtemp_arrival"] if row["Airtemp_arrival"] else None
            sample.min_air_temp = row["Airtemp_min"] if row["Airtemp_min"] else None
            sample.max_air_temp = row["Airtemp_max"] if row["Airtemp_max"] else None
            sample.percent_cloud_cov = cloud
            sample.precipitation_comment = row["Precipitation"] if row["Precipitation"] else None
            sample.wind_speed = wind_dict[row["Wind"].strip().lower()]["speed"] if row["Wind"] else None
            sample.wind_direction = wind_dict[row["Wind"].strip().lower()]["direction"] if row["Wind"] else None
            sample.water_level_delta_m = row["Water_level"] if row["Water_level"] else None
            sample.discharge_m3_sec = row["Discharge_m3_sec"] if row["Discharge_m3_sec"] else None
            sample.water_temp_c = row["Water_temperature_shore"] if row["Water_temperature_shore"] else None
            sample.water_temp_trap_c = row["VEMCO"] if row["VEMCO"] else None
            sample.rpm_arrival = row["RPM_arrival"] if row["RPM_arrival"] else None
            sample.rpm_departure = row["RPM_departure"] if row["RPM_departure"] else None
            sample.operating_condition = operating_condition_dict[row["Operating_condition"].lower().strip()] if row["Operating_condition"] else None
            sample.operating_condition_comment = row["Operating_condition"] if row["Operating_condition"] else None
            sample.samplers = row["Crew"] if row["Crew"] else None
            sample.notes = comment

            try:
                sample.save()
            except Exception as E:
                print(row["id"], E)


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
                print("big problem for specimen id={}. no sample found for site={}, date={}/{}/{}".format(
                    row["id"],
                    site,
                    row["Year"],
                    row["Month"],
                    row["Day"],
                ))

            elif samples.count() > 1:
                print("small problem for specimen id={}. multiple samples found for site={}, date={}/{}/{}".format(
                    row["id"],
                    site,
                    row["Year"],
                    row["Month"],
                    row["Day"],
                ))
                for s in samples:
                    print(s.arrival_date, row["Time.Start"])
                print("going to put all specimens in the first sample")
            if samples.exists():
                # there has been  1 or more hits and we can create the specimen in the db
                my_specimen, created = models.Entry.objects.get_or_create(
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
                    my_specimen.species = species
                    my_specimen.sample = samples.first()
                    my_specimen.first_tag = row["First.Tag"].strip() if row["First.Tag"] else None
                    my_specimen.last_tag = row["Last.Tag"].strip() if row["Last.Tag"] else None
                    my_specimen.status = status
                    my_specimen.origin = origin
                    my_specimen.frequency = row["Freq"].strip() if row["Freq"] else None
                    my_specimen.fork_length = row["ForkLength"].strip() if row["ForkLength"] else None
                    my_specimen.total_length = row["Total.Length"].strip() if row["Total.Length"] else None
                    my_specimen.weight = row["Weight"].strip() if row["Weight"] else None
                    my_specimen.sex = sex
                    my_specimen.smolt_age = row["Smolt.Age"].strip() if row["Smolt.Age"] else None
                    my_specimen.scale_id_number = row["Scale ID Number"].strip() if row["Scale ID Number"] else None
                    my_specimen.tags_removed = row["tags removed"].strip() if row["tags removed"] else None
                    my_specimen.notes = row["Comments"].strip() if row["Comments"] else None

                    try:
                        my_specimen.save()
                    except Exception as e:
                        print(e)
                        print(my_specimen.id)

            i += 1


def transfer_life_stage():
    for specimen in models.Specimen.objects.filter(species__life_stage__isnull=False):
        specimen.life_stage_id = specimen.species.life_stage_id
        specimen.save()


def clean_up_species_table():
    # first let's get a list of duplicate TSNs
    duplicate_tsns = list()

    qs = models.Species.objects.values("tsn").order_by("tsn").distinct().annotate(dcount=Count("tsn"))
    for obj in qs:
        if obj["dcount"] > 1:
            duplicate_tsns.append(obj["tsn"])

    # for each TSN, we want to keep the one with the most specimens as the authoritative
    for tsn in duplicate_tsns:
        qs = models.Species.objects.filter(tsn=tsn)
        keeper = qs.first()  # arbitrarily set to the first in line
        max_specimens = 0
        for sp in qs:
            print(sp.id, sp, sp.specimens.count())
            if sp.specimens.count() > max_specimens:
                keeper = sp
        # now that we have a keeper, transfer over the other specimens to that sp and delete bad spp
        # qs = qs.filter(~Q(id=keeper.id))
        # for sp in qs:
        #     for specimen in sp.specimens.all():
        #         specimen.species_id = keeper.id
        #         specimen.save()
        #     print(sp.specimens.count())
        # sp.delete()


def clean_up_lamprey():
    s150 = models.Species.objects.get(code=150)  # good one
    s151 = models.Species.objects.get(code=151)  # ammocoete
    s152 = models.Species.objects.get(code=152)  # silver
    life_stage_ammocoete, created = models.LifeStage.objects.get_or_create(name="ammocoete")
    life_stage_silver, created = models.LifeStage.objects.get_or_create(name="silver")

    for specimen in s151.specimens.all():
        specimen.species_id = s150.id
        specimen.life_stage_id = life_stage_ammocoete.id
        specimen.save()

    for specimen in s152.specimens.all():
        specimen.species_id = s150.id
        specimen.life_stage_id = life_stage_silver.id
        specimen.save()

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
    specimens = models.Specimen.objects.filter(scale_id_number__isnull=False)
    scale_ids = set([o.scale_id_number for o in specimens])

    for sid in scale_ids:
        if specimens.filter(scale_id_number=sid).count() > 1:
            print(f"duplicate records found for: {sid}")


def annotate_scales():
    # get the unique list of scale ids
    specimens = models.Specimen.objects.filter(scale_id_number__isnull=False)

    for o in specimens:
        o.scale_id_number += f" {o.sample.season}"
        o.save()

    find_duplicate_scales()


def populate_len():
    fl_specimens = models.Specimen.objects.filter(fork_length__isnull=False, length__isnull=True)
    for o in fl_specimens:
        o.length = o.fork_length
        o.length_type = 1
        o.save()

    tot_specimens = models.Specimen.objects.filter(total_length__isnull=False, length__isnull=True)
    for o in tot_specimens:
        o.length = o.total_length
        o.length_type = 2
        o.save()


def reverse_len():
    len_specimens = models.Specimen.objects.filter(fork_length__isnull=True, total_length__isnull=True, length__isnull=False)
    for o in len_specimens:
        if o.length_type == 1:
            o.fork_length = o.length
        else:
            o.total_length = o.length
        o.save()

    problem_specimens_1 = models.Specimen.objects.filter(fork_length__isnull=False, length__isnull=False, length_type=1)
    for o in problem_specimens_1:
        if o.length != o.fork_length:
            print("bad specimen", o.id)
    problem_specimens_2 = models.Specimen.objects.filter(total_length__isnull=False, length__isnull=False, length_type=2)
    for o in problem_specimens_2:
        if o.length != o.total_length:
            print("bad specimen", o.id)


def delete_tags_removed():
    specimens = models.Specimen.objects.filter(tags_removed__isnull=False, tag_number__isnull=False)
    for specimen in specimens:

        # get a list of tags from the removed_tags
        removed_tags = specimen.tags_removed.split(" ")
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
            # if the specimen tag number is not the same length as the reference tag number, we'll have to do some surgery
            if not digits == len(specimen.tag_number):
                # print(specimen.tag_number, "does not conform to the format of tags removed:", removed_tags)
                pos = len(specimen.tag_number) - 1
                new_tag = f"{specimen.tag_number[0]}0{specimen.tag_number[-pos:]}"
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
                    specimen.tag_number = new_tag
                    specimen.save()

            if specimen.tag_number in removed_tags:
                print("This specimen is being deleted:", specimen.tag_number, removed_tags)
                specimen.delete()


def import_smolt_ages():
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'trapnet', 'misc', 'smolt_ages_to_import.csv')
    with open(os.path.join(my_target_data_file), 'r') as csv_read_file:

        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            scale_id = row["Scale ID Number"].strip()
            qs = models.Specimen.objects.filter(scale_id_number=scale_id)
            if not qs.exists():
                scale_id = scale_id + f' {row["Year"]}'
                qs = models.Specimen.objects.filter(scale_id_number=scale_id)
                if not qs.exists():
                    print("cannot find scale number:", scale_id)
                elif qs.count() > 1:
                    print("too many results:", scale_id)
                else:
                    # print(f"ready to insert age for scale_id {scale_id}: {row['Smolt.Age']}")
                    specimen = qs.first()
                    specimen.river_age = row['Smolt.Age']
                    specimen.save()
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
                    qs = models.Specimen.objects.filter(
                        sample__site=site,
                        sample__arrival_date=arrival_date,
                        tag_number__isnull=True,
                        status__code__iexact="r",
                        river_age__isnull=True,
                        length=None,
                    )
                    print(qs.count(), freq, qs.count() > freq)
                    i = 1
                    for specimen in qs:
                        specimen.river_age = row['Smolt.Age']
                        specimen.save()
                        print("updating:", i, specimen.id)
                        qs0 = models.Specimen.objects.filter(
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
                        qs = models.Specimen.objects.filter(
                            sample__site=site,
                            sample__arrival_date=arrival_date,
                            tag_number__isnull=True,
                            status__code__iexact="r",
                            river_age__isnull=True,
                            notes__icontains=row["Comments"],
                        )
                        if qs.count() == 1:
                            specimen = qs.first()
                            specimen.river_age = row['Smolt.Age']
                            specimen.save()
                    if species == 79 and life_stage_id == "2":
                        qs = models.Specimen.objects.filter(
                            sample__site=site,
                            sample__arrival_date=arrival_date,
                            tag_number__isnull=True,
                            status__code__iexact=row["Status"],
                            river_age__isnull=True,
                            # notes__icontains=row["Comments"],
                            fork_length=row["ForkLength"]
                        )
                        if qs.count() == 1:
                            specimen = qs.first()
                            specimen.river_age = row['Smolt.Age']
                            specimen.save()

                    if species == 24:
                        qs = models.Specimen.objects.filter(
                            sample__site=site,
                            sample__arrival_date=arrival_date,
                            tag_number__isnull=True,
                            status__code__iexact=row["Status"],
                            river_age__isnull=True,
                            fork_length=row["ForkLength"]
                        )
                        print(qs.count())
                        if qs.count() == 1:
                            specimen = qs.first()
                            specimen.river_age = row['Smolt.Age']
                            specimen.save()
                    elif species == 54:
                        qs = models.Specimen.objects.filter(
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
                            specimen = qs.first()
                            specimen.river_age = row['Smolt.Age']
                            specimen.save()


def populate_adipose_condition():
    print("first part:")
    for o in models.Specimen.objects.filter(origin__code__iexact="ha"):
        o.adipose_condition = 0
        o.save()

    print("second part:")
    for o in models.Specimen.objects.filter(origin__code__iexact="w"):
        o.adipose_condition = 1
        o.save()


def check_for_didymo():
    from trapnet import models
    samples = models.Sample.objects.filter(notes__icontains="didymo")
    for sample in samples:
        remarks = sample.notes.lower()
        if "absent" in remarks:
            sample.didymo = 0
        else:
            sample.didymo = 1
        sample.save()

    samples = models.Sample.objects.filter(sweeps__notes__icontains="didymo").distinct()
    for sample in samples:
        remarks = sample.notes.lower()
        if "absent" in remarks:
            sample.didymo = 0
        else:
            sample.didymo = 1
        sample.save()


def samples_to_sub_types():
    sample_fields = [field.name for field in models.Sample._meta.fields]
    sample_fields.remove("id")

    for s in models.Sample.objects.all():
        s.save()
        if s.sample_type == 1:
            sub = s.rst_sample
        elif s.sample_type == 2:
            sub = s.ef_sample
        else:
            sub = s.trapnet_sample

        sub_fields = [f.name for f in sub._meta.fields]
        sub_fields.remove("id")
        for f in sub_fields:
            if f in sample_fields and getattr(s, f):
                setattr(sub, f, getattr(s, f))

        sub.save()
