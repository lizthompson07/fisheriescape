import os
import csv
import datetime
import pickle

from django.db import IntegrityError

from lib.templatetags.custom_filters import nz
from .. import models
from django.utils import timezone

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
                datetime.datetime.strptime("{}/{}/{}".format(row[1],row[2],row[3]), "%d/%m/%Y"),
                timezone.get_current_timezone()
            )

            my_sample, created = models.Sample.objects.get_or_create(
                old_id=row[0],
                sample_date=sample_date,
                sampler_ref_number=row[6],
            )

            # f) sampler name (text)
            search_name = row[5].replace(" ","").replace(".","").upper()
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

            # j) NAFO code
            search_name = row[9]
            for area in models.FishingArea.objects.all():
                if search_name == area.nafo_area_code:
                    my_sample.fishing_area = area
                    print("found!")
                    break

            # gear code
            search_name = row[12]
            for gear in models.Gear.objects.all():
                if search_name == gear.gear_code:
                    my_sample.gear = gear
                    print("found!")
                    break

            # l) cfvn
            # col_l = str(nz(sample.vessel_cfvn, "")).rjust(padding_lengths[11])
            #
            # # m) gear code (str)
            # if sample.gear:
            #     gear_code = sample.gear.gear_code
            #     if sample.experimental_net_used:
            #         gear_code = gear_code + "*"
            # else:
            #     gear_code = ""
            # col_m = str(gear_code).rjust(padding_lengths[12])
            #
            # # n) mesh size (float)
            # if sample.mesh_size:
            #     mesh_size = "{:.2f}".format(sample.mesh_size.size_inches_decimal)
            # else:
            #     mesh_size = ""
            # col_n = str(mesh_size).rjust(padding_lengths[13])
            #
            # # o) lat
            # if sample.latitude_n:
            #     my_var = sample.latitude_n[:6]
            # else:
            #     my_var = ""
            # col_o = str(nz(my_var, "")).rjust(padding_lengths[14])
            #
            # # p) long
            # if sample.longitude_w:
            #     my_var = sample.longitude_w[:6]
            # else:
            #     my_var = ""
            # col_p = str(nz(my_var, "")).rjust(padding_lengths[15])
            #
            # # q) landed wt.
            # if sample.catch_weight_lbs:
            #     catch_wt = int(sample.catch_weight_lbs)
            # else:
            #     catch_wt = ""
            # col_q = str(catch_wt).rjust(padding_lengths[16])
            #
            # # r) sampling protocol
            # if sample.type == 2:  # sea sample
            #     protocol = 8
            # else:  # port sample
            #     if sample.experimental_net_used:
            #         # mesh selectivity
            #         protocol = 2
            #     else:
            #         # vanilla port sampling
            #         protocol = 1
            # col_r = str(protocol).rjust(padding_lengths[17])
            #
            # # s) blank
            # col_s = str("").rjust(padding_lengths[18])
            #
            # # t) length frequency bins
            # col_t = str(0.5).rjust(padding_lengths[19])
            #
            # # u) number processed
            # col_u = str(nz(sample.total_fish_preserved, "")).rjust(padding_lengths[20])
            #
            # # v) date processed
            # col_v = str("").rjust(padding_lengths[21])
            #
            # # w) ager name
            # col_w = str("").rjust(padding_lengths[22])
            #
            # # x) comment
            # col_x = str("").rjust(padding_lengths[23])
            #
            # # y) blank
            # col_y = str("").rjust(padding_lengths[24])
            #
            # # z) maps to WHARF_CODE in oracle db
            # if sample.port:
            #     my_var = sample.port.alias_wharf_id
            # else:
            #     my_var = ""
            # col_z = str(my_var).rjust(padding_lengths[25])
            #
            # # aa) blank
            # col_aa = str("").rjust(padding_lengths[26])
            #
            # # ab) blank
            # col_ab = str("").rjust(padding_lengths[27])
            #
            #
            my_sample.save()
