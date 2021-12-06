import csv
import os

import xlsxwriter
from django.conf import settings
from django.utils import timezone

from dm_apps.utils import Echo
from lib.templatetags.custom_filters import nz
from lib.templatetags.verbose_names import get_verbose_label, get_field_value
from scuba import models


def generate_dive_log(year):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)
    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)

    # create formatting variables
    title_format = workbook.add_format({'bold': True, "align": 'normal', 'font_size': 24, })
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', "align": 'normal', "text_wrap": True})
    total_format = workbook.add_format({'bold': True, "align": 'left', "text_wrap": True, 'num_format': '$#,##0'})
    normal_format = workbook.add_format({"align": 'left', "text_wrap": True, 'border': 1, 'border_color': 'black', })
    currency_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': "yyyy-mm-dd", "align": 'left', })

    # get the dive list
    dives = models.Dive.objects.all()
    if year:
        dives = dives.filter(sample__datetime__year=year)

    field_list = [
        "datetime|Date",
        "site|Region/Site",
        "diver",
        "psi_in",
        "psi_out",
        "start_descent",
        "bottom_time",
        "max_depth_ft",
    ]

    # get_cost_comparison_dict

    # define the header
    header = [get_verbose_label(dives.first(), field) for field in field_list]
    # header.append('Number of projects tagged')
    title = "SCUBA Dive Log"

    # define a worksheet
    my_ws = workbook.add_worksheet(name="trip list")
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    i = 3
    for dive in dives.order_by("sample__datetime"):
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
        j = 0
        for field in field_list:

            if "datetime" in field:
                my_val = dive.sample.datetime.strftime("%Y-%m-%d")
                my_ws.write(i, j, my_val, date_format)
            elif "site" in field:
                my_val = f"{dive.sample.site.region.name} / {dive.sample.site.name}"
                my_ws.write(i, j, my_val, normal_format)
            else:
                my_val = str(get_field_value(dive, field))
                my_ws.write(i, j, my_val, normal_format)

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            # if new value > stored value... replace stored value
            if len(str(my_val)) > col_max[j]:
                if len(str(my_val)) < 75:
                    col_max[j] = len(str(my_val))
                else:
                    col_max[j] = 75
            j += 1
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url


def generate_transect_csv():
    """Returns a generator for an HTTP Streaming Response"""

    filter_kwargs = {}
    qs = models.Transect.objects.filter(**filter_kwargs).iterator()
    random_obj = models.Transect.objects.first()
    fields = random_obj._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)
    header_row = [field for field in field_names]  # starter
    # header_row.extend(["sample", "sample_id", "transect", "transect_id"])

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]  # starter
        # data_row.extend([obj.section.dive.sample, obj.section.dive.sample_id, obj.section.dive.sample.transect, obj.section.dive.sample.transect_id])
        yield writer.writerow(data_row)


def generate_obs_csv(year):
    """Returns a generator for an HTTP Streaming Response"""

    filter_kwargs = {}
    if year != "":
        filter_kwargs["section__dive__sample__datetime__year"] = year

    qs = models.Observation.objects.filter(**filter_kwargs).iterator()
    random_obj = models.Observation.objects.first()
    fields = random_obj._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)
    header_row = [field for field in field_names]  # starter
    header_row.extend(["sample", "sample_id", "transect", "transect_id"])

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]  # starter
        data_row.extend([obj.section.dive.sample, obj.section.dive.sample_id, obj.section.dive.sample.transect, obj.section.dive.sample.transect_id])
        yield writer.writerow(data_row)


def generate_outing_csv(year):
    """Returns a generator for an HTTP Streaming Response"""

    filter_kwargs = {}
    if year != "":
        filter_kwargs["datetime__year"] = year

    qs = models.Sample.objects.filter(**filter_kwargs).iterator()
    random_obj = models.Sample.objects.first()
    fields = random_obj._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)
    header_row = [field for field in field_names]  # starter

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]  # starter
        yield writer.writerow(data_row)


def generate_section_csv(year):
    """Returns a generator for an HTTP Streaming Response"""

    filter_kwargs = {}
    if year != "":
        filter_kwargs["dive__sample__datetime__year"] = year

    qs = models.Section.objects.filter(**filter_kwargs).iterator()
    random_obj = models.Section.objects.first()
    fields = random_obj._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)
    header_row = [field for field in field_names]  # starter
    header_row.extend(["sample", "sample_id", "date", "region", "transect", "diver", "side_display", "width_m", "interval_display"])

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]  # starter
        data_row.extend(
            [obj.dive.sample, obj.dive.sample_id, obj.dive.sample.datetime.strftime("%Y-%m-%d"), obj.dive.sample.transect.region, obj.dive.sample.transect.name,
             obj.dive.diver,
             obj.dive.get_side_display(), obj.dive.width_m, obj.get_interval_display()])
        yield writer.writerow(data_row)


def generate_dive_csv(year):
    """Returns a generator for an HTTP Streaming Response"""

    filter_kwargs = {}
    if year != "":
        filter_kwargs["sample__datetime__year"] = year

    qs = models.Dive.objects.filter(**filter_kwargs).iterator()
    random_obj = models.Dive.objects.first()
    fields = random_obj._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)
    header_row = [field for field in field_names]  # starter
    header_row.extend(["transect", "transect_id"])

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]  # starter
        data_row.extend([obj.sample.transect, obj.sample.transect_id])
        yield writer.writerow(data_row)
