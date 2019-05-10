import os
import csv
import datetime
import pickle

from django.db import IntegrityError

from lib.templatetags.custom_filters import nz
from .. import models
from django.utils import timezone

rootdir = "C:\\Users\\fishmand\\Documents\\AIS\\"

sampler_dict = {}
for s in models.Sampler.objects.all():
    sampler_dict["{} {}".format(s.first_name, s.last_name)] = s.id

probe_dict = {}
for p in models.Probe.objects.all():
    sampler_dict[p.probe_name] = p.id


# STEP 1
def seed_biofouling_samples_deployments():
    '''
    -the sample in the new db = year + substn in the old db
    -there are either 2 or three trips in a sample: first, second, full
    -date_deployed will be when protocol = 1 and retreived when protocol = 3
    '''
    # open the csv we want to read
    with open(os.path.join(rootdir, "qry_samples.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        # RERUN AND ADD TIME
        # first look at protocol = 1 to create sample
        for row in my_csv:

            deployment_date = datetime.datetime.strptime(row["eDate"].split(" ")[0], "%m/%d/%Y")
            deployment_date_tzaware = timezone.make_aware(deployment_date, timezone.get_current_timezone())
            if row['Protocol_fk'] == "1":
                my_sample, created = models.Sample.objects.get_or_create(
                    station_id=row["grais_station_id"],
                    date_deployed=deployment_date_tzaware,
                )

                if created:
                    my_sample.old_substn_id = row["SubStn_fk"]
                    my_sample.save()

                    # add samplers
                    sampler_list = row['Participants'].split(";")
                    for s in sampler_list:
                        my_sampler = models.Sampler.objects.get(pk=sampler_dict[s])
                        my_sample.samplers.add(my_sampler)

                else:
                    print("skipping")

# STEP 2
def seed_biofouling_samples_retrievals():
    '''
    -the sample in the new db = year + substn in the old db
    -there are either 2 or three trips in a sample: first, second, full
    -date_deployed will be when protocol = 1 and retreived when protocol = 3
    '''
    # open the csv we want to read
    with open(os.path.join(rootdir, "qry_samples.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            my_year = row["eDate"].split(" ")[0].split("/")[2]
            my_date_time = "{} {}".format(
                row["eDate"].split(" ")[0],
                row["Start_Time"],
            )
            retrev_date = datetime.datetime.strptime(row["eDate"].split(" ")[0], "%m/%d/%Y")
            retrev_date_tzaware = timezone.make_aware(retrev_date, timezone.get_current_timezone())
            if row['Protocol_fk'] == "3":
                try:
                    my_sample = models.Sample.objects.get(
                        station_id=row["grais_station_id"],
                        season=my_year,
                        old_substn_id=row["SubStn_fk"],
                    )
                    my_sample.date_retrieved = retrev_date_tzaware
                    my_sample.save()

                except models.Sample.DoesNotExist:
                    pass

                else:
                    # add samplers
                    sampler_list = row['Participants'].split(";")
                    for s in sampler_list:
                        my_sampler = models.Sampler.objects.get(pk=sampler_dict[s])
                        my_sample.samplers.add(my_sampler)


# STEP 3: create an eventId:SampleId dict and write to file
def event_2_sample_dict():
    with open(os.path.join(rootdir, "qry_event_to_sample.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        my_dict = {}
        for row in my_csv:
            try:
                my_sample = models.Sample.objects.get(
                    station_id=row["grais_station_id"],
                    season=row["year"],
                    old_substn_id=row["SubStn_fk"],
                )
            except models.Sample.DoesNotExist:
                print("no sample found.")

            else:
                print("hit")
                my_dict[row["Event_pk"]] = my_sample.id

        # write a pickle
        with open(os.path.join(rootdir, "event_2_sample.pickle"), 'wb') as handle:
            pickle.dump(my_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


# STEP 4: probe data
def import_probe_data():

    # import dict from pickle
    with open(os.path.join(rootdir, "event_2_sample.pickle"), 'rb') as handle:
        event_sample_dict = pickle.load(handle)

    with open(os.path.join(rootdir, "qry_probe_data.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            try:
                my_sample = models.Sample.objects.get(pk=event_sample_dict[row["Event_fk"]])
            except models.Sample.DoesNotExist:
                print("sample wasn't found.")

            try:
                my_probe = models.Probe.objects.get(pk=probe_dict[row["Data_Probe"]])
            except models.Sample.DoesNotExist:
                print("probe wasn't found.")

            my_date_time_str = row["SampleDate"] + " " + row["SampleTime"]

            probe_date = timezone.make_aware(
                datetime.datetime.strptime(my_date_time_str, "%d-%b-%Y %H:%M"),
                timezone.get_current_timezone()
            )
            retrev_date_tzaware = timezone.make_aware(retrev_date, timezone.get_current_timezone())

    #             my_sample = models.Sample.objects.get(
    #                 station_id=row["grais_station_id"],
    #                 season=row["year"],
    #                 old_substn_id=row["SubStn_fk"],
    #             )
    #         except models.Sample.DoesNotExist:
    #             print("no sample found.")
    #
    #         else:
    #             print("hit")
    #             my_dict[row["Event_pk"]] = my_sample.id
    #
    #     with open('C:\\Users\\fishmand\\Projects\\dfo_sci_dm_site\\grais\\misc\\event_2_sample.py', 'w') as file:
    #         file.write(str(my_dict))