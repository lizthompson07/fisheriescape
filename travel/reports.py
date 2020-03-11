import xlsxwriter as xlsxwriter
from django.conf import settings
from django.template.defaultfilters import yesno
from django.urls import reverse
from django.utils import timezone

from lib.functions.custom_functions import nz, listrify
from lib.functions.verbose_field_name import verbose_field_name
from lib.templatetags.custom_filters import currency
from lib.templatetags.verbose_names import get_verbose_label, get_field_value
from . import models
from shared_models import models as shared_models
import os


def generate_cfts_spreadsheet(fiscal_year=None, trip_request=None, trip=None):
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

    # get a request list
    if trip_request:
        my_trip_request = models.TripRequest.objects.get(pk=trip_request)
        if my_trip_request.is_group_request:
            is_group = True
            trip_request_list = my_trip_request.children_requests.all()
        else:
            is_group = False
            trip_request_list = models.TripRequest.objects.filter(pk=trip_request)

    elif trip:
        my_trip = models.Conference.objects.get(pk=trip)
        trip_request_list = my_trip.get_connected_requests()
    else:
        trip_request_list = None
        # non_group_trip_list = models.Trip.objects.all()

    # we need a list of ADM unapproved but recommended
    # group travellers need to be on one row

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

    if trip_request_list:
        i = 1
        for tr in trip_request_list:

            # Build the Notes field
            notes = "TRAVELLER COST BREAKDOWN: " + tr.cost_breakdown

            if tr.parent_request:
                if tr.parent_request.non_dfo_org:
                    notes += "\n\nORGANIZATIONS PAYING NON-DFO COSTS: " + tr.parent_request.non_dfo_org
            else:
                if tr.non_dfo_org:
                    notes += "\n\nORGANIZATIONS PAYING NON-DFO COSTS: " + tr.non_dfo_org

            if tr.parent_request:
                if tr.parent_request.late_justification:
                    notes += "\n\nJUSTIFICATION FOR LATE SUBMISSION: " + tr.parent_request.late_justification
            else:
                if tr.late_justification:
                    notes += "\n\nJUSTIFICATION FOR LATE SUBMISSION: " + tr.late_justification

            if tr.parent_request:
                if tr.parent_request.funding_source:
                    notes += "\n\nFUNDING SOURCE: {}".format(tr.parent_request.funding_source)
            else:
                if tr.funding_source:
                    notes += "\n\nFUNDING SOURCE: {}".format(tr.funding_source)

            # REASON
            if tr.parent_request:
                my_reason = str(tr.parent_request.reason) if tr.parent_request.reason else "n/a"
            else:
                my_reason = str(tr.reason) if tr.reason else "n/a"

            # TRIP NAME
            if tr.parent_request:
                my_trip_name = str(tr.parent_request.trip) if tr.parent_request.trip else "n/a"
            else:
                my_trip_name = str(tr.trip) if tr.trip else "n/a"

            # DESTINATION
            if tr.parent_request:
                my_dest = str(tr.parent_request.destination) if tr.parent_request.destination else "n/a"
            else:
                my_dest = str(tr.destination) if tr.destination else "n/a"

            # START DATE OF TRAVEL
            if tr.parent_request:
                my_start = tr.parent_request.start_date.strftime("%d/%m/%Y") if tr.parent_request.start_date else "n/a"
            else:
                my_start = tr.start_date.strftime("%d/%m/%Y") if tr.start_date else "n/a"

            # END DATE OF TRAVEL
            if tr.parent_request:
                my_end = tr.parent_request.end_date.strftime("%d/%m/%Y") if tr.parent_request.end_date else "n/a"
            else:
                my_end = tr.end_date.strftime("%d/%m/%Y") if tr.end_date else "n/a"

            # PURPOSE
            if tr.parent_request:
                my_purpose = tr.parent_request.purpose_long_text
            else:
                my_purpose = tr.purpose_long_text

            my_role = "{} - {}".format(
                nz(tr.role, "MISSING"),
                nz(tr.role_of_participant, "No description provided")
            )

            my_name = "{}, {}".format(tr.last_name, tr.first_name)
            if tr.is_research_scientist:
                my_name += " (RES)"

            data_row = [
                my_name,
                str(tr.region) if tr.region else "n/a",
                my_role,
                my_reason,
                my_trip_name,
                my_dest,
                my_start,
                my_end,
                tr.total_dfo_funding,
                tr.total_non_dfo_funding,
                my_purpose,
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


def generate_trip_list(fiscal_year, region, adm):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'travel', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'travel', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)

    # create formatting variables
    title_format = workbook.add_format({'bold': True, "align": 'normal', 'font_size': 24, })
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#D6D1C0', "align": 'normal', "text_wrap": True})
    total_format = workbook.add_format({'bold': True, "align": 'left', "text_wrap": True, 'num_format': '$#,##0'})
    normal_format = workbook.add_format({"align": 'left', "text_wrap": True, })

    # get the trip list
    trip_list = models.Conference.objects.filter(fiscal_year=fiscal_year)

    # optional filter on trips for adm_approval_required
    if adm != "None":
        trip_list = trip_list.filter(is_adm_approval_required=bool(int(adm)))

    # optional filter on trips for regional lead
    if region != "None":
        # too dangerous to only filter by the lead field... we should look at each request / traveller and determine
        # if they are the correct region
        request_list = list()
        # for each trip
        for trip in trip_list:
            # look at a list of the requests...
            for request in trip.trip_requests.all():
                # if group request, focus on children
                if request.is_group_request:
                    for child_request in request.children_requests.all():
                        # if the traveller is in the region of interest, add the request tp the list
                        if child_request.region_id == region:
                            # add the parent request
                            request_list.append(request)
                            break
                else:
                    # if the traveller is in the region of interest, add the request tp the list
                    if request.region_id == int(region):
                        # add the request
                        request_list.append(request)
                        break
        trip_list = trip_list.filter(trip_requests__in=request_list)

    field_list = [
        "fiscal_year",
        "name",
        "is_adm_approval_required",
        "location",
        "start_date",
        "end_date",
        "number_of_days|Number of days",
        "travellers|Travellers (cost)",
        "non_res_total_cost|Total trip cost (excluding RES)",
        "total_cost|Total trip cost",
    ]

    # get_cost_comparison_dict

    # define the header
    header = [get_verbose_label(trip_list.first(), field) for field in field_list]
    # header.append('Number of projects tagged')

    title = f"Trip List for {shared_models.FiscalYear.objects.get(pk=fiscal_year)}"
    if region != "None":
        title += f" ({shared_models.Region.objects.get(pk=region)})"

    # define a worksheet
    my_ws = workbook.add_worksheet(name=title)
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    i = 3
    for trip in trip_list:
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

        data_row = list()
        my_dict = trip.get_cost_comparison_dict
        for field in field_list:
            if "travellers" in field:
                my_list = list()
                for tr in my_dict.get("trip_requests"):
                    my_list.append(f'{tr.requester_name} ({currency(my_dict["trip_requests"][tr]["total"])})')
                data_row.append(listrify(my_list,"\n"))
            elif "fiscal_year" in field:
                data_row.append(str(get_field_value(trip, field)))
            elif "cost" in field:
                data_row.append(currency(get_field_value(trip, field)))

            else:
                data_row.append(get_field_value(trip, field))

        # adjust the width of the columns based on the max string length in each col
        ## replace col_max[j] if str length j is bigger than stored value

        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 75:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 75
            j += 1

        my_ws.write_row(i, 0, data_row, normal_format)
        print(data_row)
        my_ws.write_url(i,1,
                        url=f'{settings.SITE_FULL_URL}/{reverse("travel:trip_detail", kwargs={"pk":trip.id})}',
                        string=data_row[1])
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url
