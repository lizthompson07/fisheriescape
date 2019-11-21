import xlsxwriter as xlsxwriter
from django.conf import settings
from django.template.defaultfilters import yesno
from lib.functions.custom_functions import nz
from lib.functions.verbose_field_name import verbose_field_name
from . import models
import os


def generate_cfts_spreadsheet(fiscal_year=None, trip=None):
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
    normal_format = workbook.add_format({"align": 'left', "valign": 'top', "text_wrap": True, 'num_format': '[$$-409]#,##0.00'})

    # spreadsheet: Project List #
    #############################

    # get a project list for the year
    if trip:
        my_trip = models.Trip.objects.get(pk=trip)
        if my_trip.is_group_trip:
            is_group = True
            trip_list = my_trip.children_trips.all()
        else:
            is_group = False
            trip_list = models.Trip.objects.filter(pk=trip)
    else:
        is_group = False
        my_trip = None
        trip_list = None

    # non_group_trip_list = models.Trip.objects.all()

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
    for trip in trip_list:

        notes = "TRAVELLER COST BREAKDOWN: " + trip.cost_breakdown
        if my_trip.late_justification:
            notes += "\n\nJUSTIFICATION FOR LATE SUBMISSION: " + my_trip.late_justification

        if is_group:
            notes += "\n\nROLE OF PARTICIPANT: " + nz(trip.role_of_participant, "")

        data_row = [
            "{}, {}".format(trip.last_name, trip.first_name),
            str(trip.region) if trip.region else "n/a",
            str(trip.role) if trip.role else "n/a",
            str(my_trip.reason) if my_trip.reason else "n/a",
            my_trip.trip_title,
            my_trip.destination,
            my_trip.start_date.strftime("%d/%m/%Y"),
            my_trip.end_date.strftime("%d/%m/%Y"),
            trip.total_cost,
            "0",
            my_trip.purpose_long_text,
            notes,
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
