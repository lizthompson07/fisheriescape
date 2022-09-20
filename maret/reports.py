import os

import xlsxwriter
from django.conf import settings
from django.utils import timezone

from lib.functions.custom_functions import listrify
from lib.templatetags.verbose_names import get_verbose_label, get_field_value


def generate_interaction_report(qs):
    qs = qs.select_related("committee", "branch", "area_office", "area_office_program", "division", "lead_region",
                           "lead_national_sector", "last_modified_by")
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
    normal_format = workbook.add_format({"align": 'left', "text_wrap": False, 'border': 1, 'border_color': 'black', })

    field_list = [
        'id|Interaction Id',
        'interaction_type',
        'is_committee',
        'committee',
        'dfo_role',
        'dfo_liaison',
        'other_dfo_participants',
        'date_of_meeting',
        'main_topic',
        'species',
        'lead_region',
        'lead_national_sector',
        'branch',
        'division',
        'area_office',
        'area_office_program',
        'other_dfo_branch',
        'other_dfo_regions',
        'dfo_national_sectors',
        'other_dfo_areas',
        'action_items',
        'comments',
        'external_organization',
        'last_modified',
        'last_modified_by',
        ]

    # define the header
    header = [get_verbose_label(qs.first(), field) for field in field_list]
    title = "Filtered list of Maret Interactions"

    # define a worksheet
    my_ws = workbook.add_worksheet(name="Interactions")
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    i = 3
    for obj in qs:
        j = 0
        for field in field_list:
            # set val:
            if "interaction_type" in field:
                val = " --- "
                if obj.interaction_type:
                    val = obj.get_interaction_type_display()
            elif "date_of_meeting" in field:
                val = obj.date_of_meeting.strftime("%Y-%m-%d")
            elif "date_last_modified" in field:
                val = obj.last_modified.strftime("%Y-%m-%d")
            else:
                val = str(get_field_value(obj, field))
            # write val:
            my_ws.write(i, j, val, normal_format)

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            # if new value > stored value... replace stored value
            if len(str(val)) > col_max[j]:
                if len(str(val)) < 75:
                    col_max[j] = len(str(val))
                else:
                    col_max[j] = 75
            j += 1
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url



