import csv
import datetime
import os
from random import randint

from django.db import IntegrityError
from django.utils import timezone

from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from . import models


def delete_observations():
    models.Observation.objects.all().delete()


"""

  function extractNumber(numberStr) {
    result = ""
    for (var i = 0; i < numberStr.length; i++) {
      if (Number(numberStr[i]) || Number(numberStr[i]) === 0) {
        result += numberStr[i]
      }
    }
    return Number(result)
  }

  function extractPrefix(numberStr) {
    result = ""
    for (var i = 0; i < numberStr.length; i++) {
      if (!Number(numberStr[i])) {
        result += numberStr[i]
      }
    }
    return result
  }
"""


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


#     # remove all previous observations
# from trapnet.models import Entry
# print(Entry.objects.filter(
#     first_tag__isnull=False,
#     last_tag__isnull=False,
#     frequency__isnull=True
# ).count())
# for e in Entry.objects.filter(
#     first_tag__isnull=False,
#     last_tag__isnull=False,
#     frequency__isnull=True
# ):
#     print(e, e.first_tag, e.last_tag)

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
    # remove all previous observations
    delete_observations()
    now = timezone.now()
    for entry in models.Entry.objects.all():
        kwargs = {
            "sample": entry.sample,
            "species": entry.species,
            "status": entry.status,
            "origin": entry.origin,
            "sex": entry.sex,
            "fork_length": entry.fork_length,
            "total_length": entry.total_length,
            "weight": entry.weight,
            "age": entry.smolt_age,
            "location_tagged": entry.location_tagged,
            "date_tagged": entry.date_tagged,
            "tag_number": entry.first_tag,
            "scale_id_number": entry.scale_id_number,
            "tags_removed": entry.tags_removed,
            "notes": entry.notes,
            "created_at": now,
        }

        # determine if this is a single observation
        if not entry.last_tag and (entry.frequency == 1 or entry.frequency is None):
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


def import_smolt_1():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "smolt_import.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        # count = 0
        for row in my_csv:
            # count += 1
            # if count <= 30:
            #     print(row)

            # if there is a sample id, the major lifting is already done
            if row["sample_id"]:
                if int(row["id"]) >= 18558:
                    # just import the data
                    my_obs, created = models.Observation.objects.get_or_create(
                        id=int(row["id"]),
                    )
                    # print(row["Species"])
                    species = models.Species.objects.get(code=row["Species"]) if row["Species"] else None
                    status = models.Status.objects.get(code=row["Status"]) if row["Status"] else None
                    origin = models.Origin.objects.get(code=row["Origin"]) if row["Origin"] else None
                    sex = models.Sex.objects.get(code=row["Sex"]) if row["Sex"] else None
                    my_date = datetime.datetime.strptime(row["DateTagged"], "%m/%d/%Y") if row["DateTagged"] else None

                    my_obs.species = species
                    my_obs.sample_id = nz(row["sample_id"].strip(), None)
                    my_obs.first_tag = nz(row["FirstTag"].strip(), None)
                    my_obs.last_tag = nz(row["LastTag"].strip(), None)
                    my_obs.status = status
                    my_obs.origin = origin
                    my_obs.count = nz(row["Freq"].strip(), None)
                    my_obs.fork_length = nz(row["ForkLength"].strip(), None)
                    my_obs.total_length = nz(row["TotalLength"].strip(), None)
                    my_obs.weight = nz(row["Weight"].strip(), None)
                    my_obs.sex = sex
                    my_obs.smolt_age = nz(row["SmoltAge"].strip(), None)
                    my_obs.location_tagged = nz(row["LocationTagged"].strip(), None)
                    my_obs.date_tagged = my_date
                    my_obs.scale_id_number = nz(row["Scale ID Number"].strip(), None)
                    my_obs.tags_removed = nz(row["tags removed"].strip(), None)
                    my_obs.notes = nz(row["Comments"].strip(), None)
                    try:
                        my_obs.save()
                    except Exception as e:
                        print(e)
                        print(my_obs.species_id)


def import_smolt_2():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "smolt_import.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            # if there is no sample id, we have to assign one before creating the new observation
            if not row["sample_id"]:
                if int(row["id"]) > 0:
                    # find the sample
                    site = models.RiverSite.objects.get(pk=row["River"])

                    # check to see if there is a direct hit using only year, month, day
                    my_samples = models.Sample.objects.filter(
                        site=site,
                        arrival_date__year=int(row["Year"]),
                        arrival_date__month=int(row["Month"]),
                        arrival_date__day=int(row["Day"]),
                    )
                    if my_samples.count() == 0:
                        print("big problem for obs id={}. no sample found for site={}, date={}/{}/{}".format(
                            row["id"],
                            site,
                            row["Year"],
                            row["Month"],
                            row["Day"],
                        ))

                    elif my_samples.count() > 1:
                        print("small problem for obs id={}. multiple samples found for site={}, date={}/{}/{}".format(
                            row["id"],
                            site,
                            row["Year"],
                            row["Month"],
                            row["Day"],
                        ))
                        # try:
                        #     my_time = datetime.datetime.strptime(row["TimeStart"], "%H:%M") if row["TimeStart"] else None
                        # except ValueError:
                        #     print("bad start time given for observation {}".format(row["id"]))
                        # else:
                        #     if my_time:

                    else:
                        # there has been only 1 hit and we can create the observation in the db
                        my_obs, created = models.Entry.objects.get_or_create(
                            id=int(row["id"]),
                        )
                        if created:

                            species = models.Species.objects.get(code=row["Species"]) if row["Species"] else None
                            status = models.Status.objects.get(code=row["Status"]) if row["Status"] else None
                            origin = models.Origin.objects.get(code=row["Origin"]) if row["Origin"] else None
                            sex = models.Sex.objects.get(code=row["Sex"]) if row["Sex"] else None
                            my_date = datetime.datetime.strptime(row["DateTagged"], "%m/%d/%Y") if row["DateTagged"] else None

                            my_obs.species = species
                            my_obs.sample = my_samples.first()
                            my_obs.first_tag = nz(row["FirstTag"].strip(), None)
                            my_obs.last_tag = nz(row["LastTag"].strip(), None)
                            my_obs.status = status
                            my_obs.origin = origin
                            my_obs.frequency = nz(row["Freq"].strip(), None)
                            my_obs.fork_length = nz(row["ForkLength"].strip(), None)
                            my_obs.total_length = nz(row["TotalLength"].strip(), None)
                            my_obs.weight = nz(row["Weight"].strip(), None)
                            my_obs.sex = sex
                            my_obs.smolt_age = nz(row["SmoltAge"].strip(), None)
                            my_obs.location_tagged = nz(row["LocationTagged"].strip(), None)
                            my_obs.date_tagged = my_date
                            my_obs.scale_id_number = nz(row["Scale ID Number"].strip(), None)
                            my_obs.tags_removed = nz(row["tags removed"].strip(), None)
                            my_obs.notes = nz(row["Comments"].strip(), None)

                            try:
                                my_obs.save()
                            except Exception as e:
                                print(e)
                                print(my_obs.species_id)
