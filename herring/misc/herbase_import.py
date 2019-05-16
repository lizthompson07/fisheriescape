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
            my_sample.mesh_size_id = 10
            my_sample.type = 1
            my_sample.catch_weight_lbs = nz(row[16].replace(" ",""),None)

            # j) NAFO code
            search_name = row[9]
            for area in models.FishingArea.objects.all():
                if search_name == area.nafo_area_code:
                    my_sample.fishing_area = area
                    break

            # gear code
            search_name = row[12]
            for gear in models.Gear.objects.all():
                if search_name == gear.gear_code:
                    my_sample.gear = gear
                    break

            search_name = nz(row[25].replace(" ",""),None)
            if not search_name:
                my_sample.port_id = 5423
            else:
                for port in shared_models.Port.objects.filter(alias_wharf_id__isnull=False):
                    if int(search_name) == port.alias_wharf_id:
                        my_sample.port = port
                        break



            my_sample.save()
