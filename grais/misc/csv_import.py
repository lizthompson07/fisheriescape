import os
import csv
import datetime

from django.db import IntegrityError

from lib.templatetags.custom_filters import nz
from .. import models
from django.utils import timezone

rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"

def seed_biofouling_samples():
    '''
    -the sample in the new db = year + substn in the old db
    -there are either 2 or three trips in a sample: first, second, full
    -date_deployed will be when
    '''

    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"
    with open(os.path.join(rootdir, "green_crab_2016.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        i = 0
        for row in my_csv:
            # step 1: create a sample

            # prep some vars
            my_site = models.Site.objects.get(code=row["site_code"])
            traps_set = datetime.datetime.strptime(row["td1"], "%d/%m/%Y %H:%M")
            traps_set_tzaware = timezone.make_aware(traps_set, timezone.get_current_timezone())
            traps_fished = datetime.datetime.strptime(row["td2"], "%d/%m/%Y %H:%M")
            traps_fished_tzaware = timezone.make_aware(traps_fished, timezone.get_current_timezone())
            my_sample, created = models.GCSample.objects.get_or_create(site=my_site, traps_set=traps_set_tzaware)

            if created:
                my_sample.traps_fished = traps_fished_tzaware
                for person in row["crew"].split(","):
                    my_sample.samplers.add(person)
            else:
                # add a fishing time is there is none
                if my_sample.traps_fished is None:
                    my_sample.traps_fished = traps_fished_tzaware
                else:
                    if not my_sample.traps_fished == traps_fished_tzaware:
                        print("problem with traps_fished on line {}".format(i))
                        break

                sampler_list = [s.id for s in my_sample.samplers.all().order_by("id")]
                my_list = [int(s) for s in row["crew"].split(",")]
                my_list.sort()
                if not sampler_list == my_list:
                    for person in row["crew"].split(","):
                        try:
                            my_sample.samplers.add(person)
                        except IntegrityError:
                            print("sampler already exists in sample; sample{} - line {}".format(my_sample.id, i))

            my_sample.save()

            # step 2: create probemeasurements
            # we will have to do this twice
            for m in ["1", "2"]:
                # prep
                if m == "1":
                    td = my_sample.traps_set
                else:
                    td = my_sample.traps_fished

                # use temp as proxy to whether there is data
                if nz(row['temp' + m], None) is not None:
                    try:
                        weather_list = [int(obj) for obj in row["weather" + m].split(",")]
                    except ValueError:
                        weather_list = []
                    else:
                        weather_list.sort()

                    my_meas, created = models.GCProbeMeasurement.objects.get_or_create(sample=my_sample, time_date=td, probe_id=2)
                    if created:
                        my_meas.timezone = "ADT"
                        my_meas.temp_c = nz(row['temp' + m], None)
                        my_meas.sal = nz(row['sal' + m], None)
                        my_meas.o2_percent = nz(row['do_per' + m], None)
                        my_meas.o2_mgl = nz(row['do_mgl' + m], None)
                        my_meas.sp_cond_ms = nz(row['spc' + m], None)
                        my_meas.cond_ms = nz(row['cond' + m], None)
                        my_meas.tide_state = nz(row['tide_state' + m], None)
                        my_meas.tide_direction = nz(row['tide_dir' + m], None)
                        my_meas.cloud_cover = nz(row['cloud' + m], None)
                        print(weather_list)
                        for cond in weather_list:
                            my_meas.weather_conditions.add(cond)
                        my_meas.save()

            # step 2: create traps
            my_trap, created = models.Trap.objects.get_or_create(
                sample=my_sample,
                trap_number=row['trap_number'],
                trap_type=row['trap_type'],
                bait_type=row['bait_type'],
            )
            if created:
                my_trap.depth_at_set_m = nz(row['depth'], None)
                my_trap.latitude_n = nz(row['lat'], None)
                my_trap.longitude_w = nz(row['long'], None)
                my_trap.gps_waypoint = nz(row['gps'], None)
                my_trap.notes = nz(row['notes'], None)
                my_trap.total_green_crab_wt_kg = nz(row['total_wt_kg'], None)
                my_trap.save()
            i += 1


def seed_crabs_db():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"
    with open(os.path.join(rootdir, "green_crab_2016.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        i = 0
        for row in my_csv:
            if row['type']=="Crab":
                # prep some vars
                my_site = models.Site.objects.get(code=row["site_code"])
                traps_set = datetime.datetime.strptime(row["td1"], "%d/%m/%Y %H:%M")
                traps_set_tzaware = timezone.make_aware(traps_set, timezone.get_current_timezone())
                try:
                    my_sample = models.GCSample.objects.get(site=my_site, traps_set=traps_set_tzaware)
                except models.GCSample.DoesNotExist:
                    print(row)
                    print(i)
                    print(my_site)
                    print(traps_set_tzaware)
                    break
                # green crabs
                my_trap = models.Trap.objects.get(
                    sample=my_sample,
                    trap_number=row['trap_number'],
                )
                if nz(row['gc_no'], None):
                    my_crab = models.Crab.objects.create(
                        species_id=26,
                        trap=my_trap,
                        width=nz(row['gc_width'], None),
                        sex=nz(row['gc_sex'], None),
                        carapace_color=nz(row['gc_carapace'], None),
                        abdomen_color=nz(row['gc_adbomen'], None),
                        egg_color=nz(row['gc_egg'], None),
                        notes=nz(row['notes'], None),
                    )
                    my_crab.save()
                    print("adding green crab from line {} - sample {} - trap {}".format(i, my_sample.id, my_trap.id))

                if nz(row['rc_no'], None):
                    my_crab = models.Crab.objects.create(
                        species_id=96,
                        trap=my_trap,
                        width=nz(row['rc_width'], None),
                        sex=nz(row['rc_sex'], None),
                    )
                    my_crab.save()
                    print("adding rock crab from line {} - sample {} - trap {}".format(i, my_sample.id, my_trap.id))

                if nz(row['bm_no'], None):
                    my_crab = models.Crab.objects.create(
                        species_id=98,
                        trap=my_trap,
                        width=nz(row['bm_width'], None),
                        sex=nz(row['bm_sex'], None),
                    )
                    my_crab.save()
                    print("adding white crab from line {} - sample {} - trap {}".format(i, my_sample.id, my_trap.id))


                if nz(row['wm_no'], None):
                    my_crab = models.Crab.objects.create(
                        species_id=27,
                        trap=my_trap,
                        width=nz(row['wm_width'], None),
                        sex=nz(row['wm_sex'], None),
                    )
                    my_crab.save()
                    print("adding black crab from line {} - sample {} - trap {}".format(i, my_sample.id, my_trap.id))

            i += 1

def seed_bycatch():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"
    with open(os.path.join(rootdir, "green_crab_2016.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        i = 0
        for row in my_csv:
            if i > 8100:
                # prep some vars
                my_site = models.Site.objects.get(code=row["site_code"])
                traps_set = datetime.datetime.strptime(row["td1"], "%d/%m/%Y %H:%M")
                traps_set_tzaware = timezone.make_aware(traps_set, timezone.get_current_timezone())
                try:
                    my_sample = models.GCSample.objects.get(site=my_site, traps_set=traps_set_tzaware)
                except models.GCSample.DoesNotExist:
                    print(i)
                    print(my_site)
                    print(traps_set_tzaware)
                    break

                # bycatch
                try:
                    my_trap = models.Trap.objects.get(
                        sample=my_sample,
                        trap_number=row['trap_number'],
                    )
                except (models.Trap.DoesNotExist, models.Trap.MultipleObjectsReturned):
                    print(i)
                    print(my_sample)
                    print("trap_number={}".format(row['trap_number']))
                    break

                spp_list = [
                    85,
                    86,
                    87,
                    81,
                    89,
                    90,
                    33,
                    91,
                    102,
                    92,
                    93,
                    94,
                    95,
                    103,
                ]
                for s in spp_list:
                    my_spp = models.Species.objects.get(pk=s)
                    if nz(row['sp_{}'.format(s)], None):
                        try:
                            my_bycatch = models.Bycatch.objects.create(
                                species=my_spp,
                                trap=my_trap,
                                count=int(row['sp_{}'.format(s)]),
                            )
                        except IntegrityError:
                            print("skipping...")
                        else:
                            my_bycatch.save()
                            print("adding {} from line {} - sample {} - trap {}".format(my_spp, i, my_sample.id, my_trap.id))

            i += 1





# open the csv we want to read

def seed_db():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"
    with open(os.path.join(rootdir, "green_crab_2016.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        i = 0
        for row in my_csv:
            # step 1: create a sample

            # prep some vars
            my_site = models.Site.objects.get(code=row["site_code"])
            traps_set = datetime.datetime.strptime(row["td1"], "%d/%m/%Y %H:%M")
            traps_set_tzaware = timezone.make_aware(traps_set, timezone.get_current_timezone())
            traps_fished = datetime.datetime.strptime(row["td2"], "%d/%m/%Y %H:%M")
            traps_fished_tzaware = timezone.make_aware(traps_fished, timezone.get_current_timezone())
            my_sample, created = models.GCSample.objects.get_or_create(site=my_site, traps_set=traps_set_tzaware)

            if created:
                my_sample.traps_fished = traps_fished_tzaware
                for person in row["crew"].split(","):
                    my_sample.samplers.add(person)
            else:
                # add a fishing time is there is none
                if my_sample.traps_fished is None:
                    my_sample.traps_fished = traps_fished_tzaware
                else:
                    if not my_sample.traps_fished == traps_fished_tzaware:
                        print("problem with traps_fished on line {}".format(i))
                        break

                sampler_list = [s.id for s in my_sample.samplers.all().order_by("id")]
                my_list = [int(s) for s in row["crew"].split(",")]
                my_list.sort()
                if not sampler_list == my_list:
                    for person in row["crew"].split(","):
                        try:
                            my_sample.samplers.add(person)
                        except IntegrityError:
                            print("sampler already exists in sample; sample{} - line {}".format(my_sample.id, i))

            my_sample.save()

            # step 2: create probemeasurements
            # we will have to do this twice
            for m in ["1", "2"]:
                # prep
                if m == "1":
                    td = my_sample.traps_set
                else:
                    td = my_sample.traps_fished

                # use temp as proxy to whether there is data
                if nz(row['temp' + m], None) is not None:
                    try:
                        weather_list = [int(obj) for obj in row["weather" + m].split(",")]
                    except ValueError:
                        weather_list = []
                    else:
                        weather_list.sort()

                    my_meas, created = models.GCProbeMeasurement.objects.get_or_create(sample=my_sample, time_date=td, probe_id=2)
                    if created:
                        my_meas.timezone = "ADT"
                        my_meas.temp_c = nz(row['temp' + m], None)
                        my_meas.sal = nz(row['sal' + m], None)
                        my_meas.o2_percent = nz(row['do_per' + m], None)
                        my_meas.o2_mgl = nz(row['do_mgl' + m], None)
                        my_meas.sp_cond_ms = nz(row['spc' + m], None)
                        my_meas.cond_ms = nz(row['cond' + m], None)
                        my_meas.tide_state = nz(row['tide_state' + m], None)
                        my_meas.tide_direction = nz(row['tide_dir' + m], None)
                        my_meas.cloud_cover = nz(row['cloud' + m], None)
                        print(weather_list)
                        for cond in weather_list:
                            my_meas.weather_conditions.add(cond)
                        my_meas.save()

            # step 2: create traps
            my_trap, created = models.Trap.objects.get_or_create(
                sample=my_sample,
                trap_number=row['trap_number'],
                trap_type=row['trap_type'],
                bait_type=row['bait_type'],
            )
            if created:
                my_trap.depth_at_set_m = nz(row['depth'], None)
                my_trap.latitude_n = nz(row['lat'], None)
                my_trap.longitude_w = nz(row['long'], None)
                my_trap.gps_waypoint = nz(row['gps'], None)
                my_trap.notes = nz(row['notes'], None)
                my_trap.total_green_crab_wt_kg = nz(row['total_wt_kg'], None)
                my_trap.save()
            i += 1


def seed_crabs_db():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"
    with open(os.path.join(rootdir, "green_crab_2016.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        i = 0
        for row in my_csv:
            if row['type']=="Crab":
                # prep some vars
                my_site = models.Site.objects.get(code=row["site_code"])
                traps_set = datetime.datetime.strptime(row["td1"], "%d/%m/%Y %H:%M")
                traps_set_tzaware = timezone.make_aware(traps_set, timezone.get_current_timezone())
                try:
                    my_sample = models.GCSample.objects.get(site=my_site, traps_set=traps_set_tzaware)
                except models.GCSample.DoesNotExist:
                    print(row)
                    print(i)
                    print(my_site)
                    print(traps_set_tzaware)
                    break
                # green crabs
                my_trap = models.Trap.objects.get(
                    sample=my_sample,
                    trap_number=row['trap_number'],
                )
                if nz(row['gc_no'], None):
                    my_crab = models.Crab.objects.create(
                        species_id=26,
                        trap=my_trap,
                        width=nz(row['gc_width'], None),
                        sex=nz(row['gc_sex'], None),
                        carapace_color=nz(row['gc_carapace'], None),
                        abdomen_color=nz(row['gc_adbomen'], None),
                        egg_color=nz(row['gc_egg'], None),
                        notes=nz(row['notes'], None),
                    )
                    my_crab.save()
                    print("adding green crab from line {} - sample {} - trap {}".format(i, my_sample.id, my_trap.id))

                if nz(row['rc_no'], None):
                    my_crab = models.Crab.objects.create(
                        species_id=96,
                        trap=my_trap,
                        width=nz(row['rc_width'], None),
                        sex=nz(row['rc_sex'], None),
                    )
                    my_crab.save()
                    print("adding rock crab from line {} - sample {} - trap {}".format(i, my_sample.id, my_trap.id))

                if nz(row['bm_no'], None):
                    my_crab = models.Crab.objects.create(
                        species_id=98,
                        trap=my_trap,
                        width=nz(row['bm_width'], None),
                        sex=nz(row['bm_sex'], None),
                    )
                    my_crab.save()
                    print("adding white crab from line {} - sample {} - trap {}".format(i, my_sample.id, my_trap.id))


                if nz(row['wm_no'], None):
                    my_crab = models.Crab.objects.create(
                        species_id=27,
                        trap=my_trap,
                        width=nz(row['wm_width'], None),
                        sex=nz(row['wm_sex'], None),
                    )
                    my_crab.save()
                    print("adding black crab from line {} - sample {} - trap {}".format(i, my_sample.id, my_trap.id))

            i += 1

def seed_bycatch():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"
    with open(os.path.join(rootdir, "green_crab_2016.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        i = 0
        for row in my_csv:
            if i > 8100:
                # prep some vars
                my_site = models.Site.objects.get(code=row["site_code"])
                traps_set = datetime.datetime.strptime(row["td1"], "%d/%m/%Y %H:%M")
                traps_set_tzaware = timezone.make_aware(traps_set, timezone.get_current_timezone())
                try:
                    my_sample = models.GCSample.objects.get(site=my_site, traps_set=traps_set_tzaware)
                except models.GCSample.DoesNotExist:
                    print(i)
                    print(my_site)
                    print(traps_set_tzaware)
                    break

                # bycatch
                try:
                    my_trap = models.Trap.objects.get(
                        sample=my_sample,
                        trap_number=row['trap_number'],
                    )
                except (models.Trap.DoesNotExist, models.Trap.MultipleObjectsReturned):
                    print(i)
                    print(my_sample)
                    print("trap_number={}".format(row['trap_number']))
                    break

                spp_list = [
                    85,
                    86,
                    87,
                    81,
                    89,
                    90,
                    33,
                    91,
                    102,
                    92,
                    93,
                    94,
                    95,
                    103,
                ]
                for s in spp_list:
                    my_spp = models.Species.objects.get(pk=s)
                    if nz(row['sp_{}'.format(s)], None):
                        try:
                            my_bycatch = models.Bycatch.objects.create(
                                species=my_spp,
                                trap=my_trap,
                                count=int(row['sp_{}'.format(s)]),
                            )
                        except IntegrityError:
                            print("skipping...")
                        else:
                            my_bycatch.save()
                            print("adding {} from line {} - sample {} - trap {}".format(my_spp, i, my_sample.id, my_trap.id))

            i += 1


