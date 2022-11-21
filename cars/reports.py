import os
from io import BytesIO
import xlsxwriter
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import activate, deactivate, gettext as _
from docx import Document

from dm_apps import settings
from lib.functions.custom_functions import listrify
from lib.templatetags.verbose_names import get_verbose_label, get_field_value
from . import models


def generate_vehicle_report(qs, site_url):
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
    normal_format = workbook.add_format({"align": 'left', "text_wrap": True, 'border': 1, 'border_color': 'black', })
    hyperlink_format = workbook.add_format({'border': 1, 'border_color': 'black', "font_color": "blue", "underline": True, "text_wrap": True})

    field_list = [

        "display",
        "location",
        "custodian",
        "section",
        "vehicle_type",
        "reference_number",
        "make",
        "model",
        "year",
        "max_passengers",
        "is_active",
        "comments",

    ]

    # define the header
    header = [get_verbose_label(qs.first(), field) for field in field_list]
    title = "Vehicle and Custodian Report"

    # define a worksheet
    my_ws = workbook.add_worksheet(name="report")
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    i = 3
    for obj in qs:
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
        j = 0
        for field in field_list:

            if "custodian office" in field or "vehicle_type" in field:
                my_val = str(obj.custodian)
                my_ws.write(i, j, my_val, normal_format)

            elif "display" in field:
                my_val = str(obj)
                my_ws.write_url(i, j,
                                url=f'{site_url}/{reverse("cars:vehicle_detail", args=[obj.id])}',
                                string=f"{my_val}",
                                cell_format=hyperlink_format)
            else:
                my_val = str(get_field_value(obj, field))
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

