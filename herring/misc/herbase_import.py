import os
import csv
import datetime
import pickle

from django.db import IntegrityError

from lib.templatetags.custom_filters import nz
from .. import models
from django.utils import timezone
from shared_models import models as shared_models

rootdir = "C:\\Users\\fishmand\\Documents\\herring\\"


# sampler_dict = {}
# for s in models.Sampler.objects.all():
#     sampler_dict["{} {}".format(s.first_name, s.last_name)] = s.id
#
# probe_dict = {}
# for p in models.Probe.objects.all():
#     probe_dict[p.probe_name] = p.id

# STEP 1
def import_hlog():
    # open the csv we want to read
    with open(os.path.join(rootdir, "hlog2018.csv"), 'r') as csv_read_file:
        my_csv = csv.reader(csv_read_file)
        # RERUN AND ADD TIME
        # first look at protocol = 1 to create sample
        for row in my_csv:
            # each row will result in a sample
            sample_date = timezone.make_aware(
                datetime.datetime.strptime("{}/{}/{}".format(row[1], row[2], row[3]).replace(" ", ""), "%d/%m/%Y"),
                timezone.get_current_timezone()
            )

            my_sample, created = models.Sample.objects.get_or_create(
                old_id=row[0],
                sample_date=sample_date,
                sampler_ref_number=row[6],
            )

            # f) sampler name (text)
            search_name = row[5].replace(" ", "").replace(".", "").upper()
            for sampler in models.Sampler.objects.all():
                if sampler.first_name:
                    compare_name = "{}{}".format(sampler.first_name[:1], sampler.last_name).upper()
                else:
                    compare_name = "{}".format(sampler.last_name).upper()

                if search_name == compare_name:
                    my_sample.sampler = sampler
                    break

            # easy ones
            my_sample.total_fish_measured = row[7]
            my_sample.total_fish_preserved = row[8]
            my_sample.vessel_cfvn = row[11]
            my_sample.mesh_size_id = 10
            my_sample.type = 1
            my_sample.catch_weight_lbs = nz(row[16].replace(" ", ""), None)
            my_sample.experimental_net_used = False
            my_sample.last_modified_by_id = 50

            # j) NAFO code
            search_name = row[9]
            for area in models.FishingArea.objects.all():
                if search_name == area.nafo_area_code:
                    my_sample.fishing_area = area
                    break

            # gear code
            search_name = row[12].strip()
            for gear in models.Gear.objects.all():
                if search_name == gear.gear_code:
                    my_sample.gear = gear
                    print("found gear!")
                    break

            search_name = nz(row[25].replace(" ", ""), None)
            if not search_name:
                my_sample.port_id = 5423
            else:
                for port in shared_models.Port.objects.filter(alias_wharf_id__isnull=False):
                    if int(search_name) == port.alias_wharf_id:
                        my_sample.port = port
                        break

            my_sample.save()


def import_hdet():
    # open the csv we want to read
    with open(os.path.join(rootdir, "hdet2018.csv"), 'r') as csv_read_file:
        my_csv = csv.reader(csv_read_file)
        # RERUN AND ADD TIME
        # first look at protocol = 1 to create sample
        for row in my_csv:
            # each row will result in a lab sample

            # get the sample
            my_sample = models.Sample.objects.get(
                old_id=row[0],
                season=2018,
            )

            lab_sample_date = timezone.make_aware(
                datetime.datetime.strptime("{}/{}/{}".format(row[1], row[2], row[3]).replace(" ", ""), "%d/%m/%Y"),
                timezone.get_current_timezone()
            )

            my_fish, created = models.FishDetail.objects.get_or_create(
                sample=my_sample,
                fish_number=int(row[4]),
            )

            my_sex = models.Sex.objects.get(oracle_code=row[7])

            try:
                my_os = models.OtolithSeason.objects.get(oracle_code=row[10])
            except models.OtolithSeason.DoesNotExist:
                print("otolith season: {}".format(row[10]))
                my_os = models.OtolithSeason.objects.get(oracle_code="I")

            mat_id = int(row[8])
            if mat_id == 0:
                mat_id = 9

            try:
                gw = float(row[9])
            except ValueError:
                print("gonad weight: {}".format(row[9]))
                gw = None

            try:
                ac = int(row[11])
            except ValueError:
                print("annulus count: {}".format(row[11]))
                ac = None

            my_fish.fish_length = float(row[5])
            my_fish.fish_weight = float(row[6])
            my_fish.gonad_weight = gw
            my_fish.sex = my_sex
            my_fish.maturity_id = mat_id
            my_fish.otolith_season = my_os
            my_fish.annulus_count = ac
            my_fish.remarks = row[13]
            my_fish.lab_processed_date = lab_sample_date
            my_fish.otolith_processed_date = lab_sample_date
            my_fish.lab_sampler_id = 371
            my_fish.otolith_sampler_id = 371
            my_fish.creation_date = timezone.now()
            my_fish.created_by_id = 50
            my_fish.last_modified_date = timezone.now()
            my_fish.last_modified_by_id = 50

            my_fish.save()


def import_hlen():
    # open the csv we want to read
    with open(os.path.join(rootdir, "hlen2018.csv"), 'r') as csv_read_file:
        my_csv = csv.reader(csv_read_file)
        # RERUN AND ADD TIME
        # first look at protocol = 1 to create sample
        for row in my_csv:
            # each row will result in a lab sample

            # get the sample
            try:
                my_sample = models.Sample.objects.get(
                    old_id=row[0],
                    season=2018,
                )
            except models.Sample.DoesNotExist:
                print("id = {}".format(row[0]))
            else:
                my_bin_starter = int(row[4])
                # for each count we will add an observation
                i = 1
                bin_interval = 0.5
                for count in row[5:15]:
                    my_count = int(count)
                    if my_count > 0:
                        my_bin = my_bin_starter + (i * bin_interval)

                        try:
                            my_lf, created = models.LengthFrequency.objects.get_or_create(
                                sample=my_sample,
                                length_bin_id=my_bin,
                                count=my_count,
                            )
                        except IntegrityError:
                            print("INTEGRITY old_id={}; len_bin={}; count={}".format(
                                row[0],
                                my_bin,
                                my_count,
                            ))
                        else:
                            if not created:
                                print("old_id={}; len_bin={}; count={}".format(
                                    row[0],
                                    my_bin,
                                    my_count,
                                ))
                    i += 1


def resave_samples():
    # open the csv we want to read
    with open(os.path.join(rootdir, "hlen2018.csv"), 'r') as csv_read_file:
        my_csv = csv.reader(csv_read_file)
        # RERUN AND ADD TIME
        # first look at protocol = 1 to create sample
        for row in my_csv:
            # each row will result in a lab sample

            # get the sample
            try:
                my_sample = models.Sample.objects.get(
                    old_id=row[0],
                    season=2018,
                )
            except models.Sample.DoesNotExist:
                print("id = {}".format(row[0]))
            else:
                my_sample.save()


def fix_hlen_():
    my_samples = [13725,
                  13726,
                  13727,
                  13729,
                  13730,
                  13731,
                  13732,
                  13733,
                  13734,
                  13735,
                  13736,
                  13737,
                  13738,
                  13739,
                  13752,
                  13753,
                  13754,
                  13756,
                  13757,
                  13759,
                  13760,
                  13761,
                  13762,
                  13763,
                  13764,
                  13765,
                  13766,
                  13767,
                  13768,
                  13769,
                  13770,
                  13771,
                  13772,
                  13773,
                  13774,
                  13775,
                  13776,
                  13777,
                  13778,
                  13779,
                  13780,
                  13781,
                  13782,
                  13783,
                  13784,
                  13785,
                  13786,
                  13787,
                  13788,
                  13789,
                  13790,
                  13791,
                  13792,
                  13793,
                  13794,
                  13795,
                  13796,
                  13797,
                  13798,
                  13799,
                  13800,
                  13801,
                  13802,
                  13803,
                  13804,
                  13805,
                  13806,
                  13807,
                  13808,
                  13809,
                  13810,
                  13811,
                  13812,
                  13813,
                  13814,
                  13815,
                  13816,
                  13817,
                  13818,
                  13819,
                  13820,
                  13821,
                  13822,
                  13823,
                  13824,
                  13825,
                  13826,
                  13827,
                  13828,
                  13829,
                  13830,
                  13832,
                  13833,
                  13834,
                  13835,
                  13836,
                  13837,
                  13838,
                  13839,
                  13840,
                  13841,
                  13842,
                  13843,
                  13844,
                  13845,
                  13846,
                  13847,
                  13848,
                  13849,
                  13850,
                  13851,
                  13852,
                  13853,
                  13854,
                  13855,
                  13856,
                  13857,
                  13858,
                  13859,
                  13860,
                  13861,
                  13862,
                  13863,
                  13864,
                  13865,
                  13866,
                  13867,
                  13868,
                  13869,
                  13870,
                  13871,
                  13872,
                  13873,
                  13874,
                  13875,
                  13876,
                  13877,
                  13878,
                  13879,
                  13880,
                  13881,
                  13882,
                  13883,
                  13884,
                  13885,
                  13886,
                  13887,
                  13888,
                  13889,
                  13890,
                  13905,
                  13906,
                  13907,
                  13908,
                  13909,
                  13910,
                  ]
    my_qs = models.LengthFrequency.objects.filter(sample_id__in=my_samples)
    my_qs.delete()

    with open(os.path.join(rootdir, "qry_hlen_replace.csv"), 'r') as csv_read_file:
        my_csv = csv.reader(csv_read_file)
        for row in my_csv:
            # each row will result in a lf to be readded
            if row[0]!= "id":
                try:
                    models.LengthFrequency.objects.create(
                        sample_id=row[1],
                        length_bin_id=row[2],
                        count=row[3],
                    )
                except IntegrityError:
                    print("not importing sample {}".format(row[1]))