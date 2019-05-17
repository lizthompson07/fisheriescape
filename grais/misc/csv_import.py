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
    probe_dict[p.probe_name] = p.id


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
            # there are some stations we are crunching. example,

            try:
                my_sample = models.Sample.objects.get(
                    station_id=row["grais_station_id"],
                    season=row["year"],
                    # old_substn_id=row["SubStn_fk"],
                )
            except models.Sample.DoesNotExist:
                print("no sample found.")

            except models.Sample.MultipleObjectsReturned:
                print([s for s in models.Sample.objects.filter(
                    station_id=row["grais_station_id"],
                    season=row["year"],
                )])

                my_sample = models.Sample.objects.filter(
                    station_id=row["grais_station_id"],
                    season=row["year"],
                ).last()
                my_dict[row["Event_pk"]] = my_sample.id

            else:
                # print("hit")
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
                print("sample wasn't found. event id = {}".format(row["Event_fk"]))
                break

            try:
                my_probe = models.Probe.objects.get(pk=probe_dict[row["Data_Probe"]])
            except models.Sample.DoesNotExist:
                print("probe wasn't found. probe name = {}".format(row["Data_Probe"]))
                break

            # get the time date from row
            my_date_time_str = row["SampleDate"] + " " + row["SampleTime"]
            probe_date = timezone.make_aware(
                datetime.datetime.strptime(my_date_time_str, "%d-%b-%y %H:%M"),
                timezone.get_current_timezone()
            )

            # get or create an instance of probe measurement
            my_probe_measurement, created = models.ProbeMeasurement.objects.get_or_create(
                sample=my_sample,
                probe=my_probe,
                time_date=probe_date,
            )

            if created:
                my_probe_measurement.probe_depth = nz(row["Probe_Depth"], None)
                my_probe_measurement.weather_notes = row["eWeather"]

            else:
                pass
                # print("not creating probe measurement")

            try:
                float(row["DataValue"])
                float(row["Probe_Depth"])
            except ValueError:
                print(row["DataValue"])
                print(row["Probe_Depth"])
                break

            # populate the value
            if row["DataType_fk"] == '1':
                my_probe_measurement.temp_c = row["DataValue"]
            elif row["DataType_fk"] == '2':
                my_probe_measurement.sal_ppt = row["DataValue"]
            elif row["DataType_fk"] == '3':
                my_probe_measurement.o2_percent = row["DataValue"]
            elif row["DataType_fk"] == '4':
                my_probe_measurement.o2_mgl = row["DataValue"]
            elif row["DataType_fk"] == '5':
                my_probe_measurement.spc_ms = row["DataValue"]
            elif row["DataType_fk"] == '6':
                my_probe_measurement.sp_cond_ms = row["DataValue"]
            else:
                print("dont know what kind of probe this is: {}".format(row["DataType_fk"]))

            my_probe_measurement.save()


# STEP 5: Import the lines
def import_lines_and_surfaces():
    # import dict from pickle
    with open(os.path.join(rootdir, "event_2_sample.pickle"), 'rb') as handle:
        event_sample_dict = pickle.load(handle)

    with open(os.path.join(rootdir, "qry_lines.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            try:
                my_sample = models.Sample.objects.get(pk=event_sample_dict[row["Event_pk"]])
            except models.Sample.DoesNotExist:
                print("sample wasn't found. event id = {}".format(row["Event_pk"]))
                break

            # get or create an instance of line
            my_line, created = models.Line.objects.get_or_create(
                sample=my_sample,
                latitude_n=row["Latitude"],
                longitude_w=row["Longitude"],
                collector="collector {}".format(row["Collector"]),
            )

            # create a corresponding surface
            PETRI = 'pe'
            PLATE = 'pl'
            if row["CollectorType_fk"] == '1':
                my_surface_type = PLATE
            elif row["CollectorType_fk"] == '2':
                my_surface_type = PETRI
            else:
                print("invalid surface type")
                break

            my_surface, created = models.Surface.objects.get_or_create(
                line=my_line,
                surface_type=my_surface_type,
                label="{} {}".format(row["Name"], row["Plate"]),
                is_lost=row["Lost"],
            )

            my_surface.old_plateheader_id = row["PlateHeader_pk"]
            my_surface.save()




# import the surface species
def import_surface_spp():
    # This is for the invasive spp only.

    with open(os.path.join(rootdir, "qry_surface_spp.csv"), 'r') as csv_read_file: # NOT CREATED
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            # get the surface
            # the platerheader id == surface id
            my_surface = models.Surface.objects.get(old_plateheader_id=int(row["PlateHeader_fk"]))

            percent_coverage = (20 * int(row["Coverage_fk"])) / 100

            notes = "This record was imported from the old database. Percent coverage is an approximated. The calculation was based on the old coverage category where 1=20%; 2=40%; 3=60%; 4=80%; 5=100%."
            if row["spDescription"] is not None and row["spDescription"] != "":
                notes = "{} The color description for this species is: {}.".format(
                    notes,
                    row["spDescription"],
                )

            my_surface_spp, created = models.SurfaceSpecies.objects.get_or_create(
                species=models.Species.objects.get(pk=row["grais_species_id"]),
                surface=my_surface,
                percent_coverage=percent_coverage,
                notes=notes,
            )
