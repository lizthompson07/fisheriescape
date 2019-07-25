import csv
import datetime
import os

from lib.templatetags.custom_filters import nz
from . import models
from shared_models import models as shared_models


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