import xlsxwriter as xlsxwriter
from django.conf import settings
from django.template.defaultfilters import yesno
from lib.functions.custom_functions import nz
from lib.functions.verbose_field_name import verbose_field_name
from . import models
import os


def generate_cfts_spreadsheet(fiscal_year):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'travel', 'temp')
    target_file = "temp_export.xlsx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'travel', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    ws = workbook.add_worksheet(name="CFTS report")

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'normal',
         "text_wrap": True})
    total_format = workbook.add_format({'bg_color': '#D6D1C0', "align": 'left', "text_wrap": True})
    normal_format = workbook.add_format({"align": 'left', "text_wrap": True})
    bold_format = workbook.add_format({"align": 'center', 'bold': True})

    # spreadsheet: Project List #
    #############################

    # get a project list for the year
    non_group_trip_list = models.Event.objects.filter(fiscal_year_id=fiscal_year, parent_event__isnull=True, is_group_trip=False)

    # we need a list of ADM unapproaved but recommended
    # group travdellers need to be on one row

    header = [
        "Name",
        "Region",
        "Primary Role of Traveller",
        "Primary Reason for Travel",
        "Event",
        "Location",
        "Start Date",
        "End Date",
        "Est. DFO Cost",
        "Est. Non-DFO Cost",
        "Purpose",
        "Notes",
    ]

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    ws.write_row(0, 0, header, header_format)

    i = 1
    for e in event_list:

        try:
            section = p.section.name
        except:
            section = "MISSING"

        data_row = [

            "{}, {}".format(e.last_name,e.first_name),
            "Gulf",
            str(e.role),
            str(e.reason),
            e.trip_title,
            e.destination,
            e.start_date.strftime("%d/%m/%Y"),
            e.end_date.strftime("%d/%m/%Y"),
            e.total_cost,
            "0",
            e.purpose_long_text,
            e.cost_breakdown,
        ]

        # adjust the width of the columns based on the max string length in each col
        ## replace col_max[j] if str length j is bigger than stored value

        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 100:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 100
            j += 1

        ws.write_row(i, 0, data_row, normal_format)
        i += 1

    for j in range(0, len(col_max)):
        ws.set_column(j, j, width=col_max[j] * 1.1)


    workbook.close()
    return target_url

