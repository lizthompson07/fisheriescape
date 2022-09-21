import os

import xlsxwriter
from django.conf import settings
from django.utils import timezone

from lib.templatetags.verbose_names import get_verbose_label, get_field_value


class InteractionReportMixin:
    select_fk_fields = ["committee", "branch", "area_office", "area_office_program", "division", "lead_region",
                        "lead_national_sector", "last_modified_by"]
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
    title = "Filtered list of Maret Interactions"
    sheet_title = "Interactions"

    def val(obj, field):
        val = " --- "
        if "interaction_type" in field:
            if obj.interaction_type:
                val = obj.get_interaction_type_display()
        elif "date_of_meeting" in field:
            if obj.date_of_meeting:
                val = obj.date_of_meeting.strftime("%Y-%m-%d")
        elif "last_modified" == field:
            if obj.last_modified:
                val = obj.last_modified.strftime("%Y-%m-%d")
        else:
            val = str(get_field_value(obj, field))
        return val


class CommitteeReportMixin:
    select_fk_fields = ["branch", "division", "area_office", "area_office_program", "division", "lead_region",
                        "lead_national_sector", "last_modified_by"]
    field_list = [
        'id|Interaction Id',
        'name',
        'main_topic',
        'species',
        'lead_region',
        'lead_national_sector',
        'branch',
        'division',
        'area_office',
        'area_office_program',
        'is_dfo_chair',
        'external_chair',
        'dfo_liaison',
        'other_dfo_branch',
        'other_dfo_regions',
        'dfo_national_sectors',
        'other_dfo_areas',
        'dfo_role',
        'first_nation_participation',
        'municipal_participation',
        'provincial_participation',
        'other_federal_participation',
        'other_dfo_participants',
        'meeting_frequency',
        'are_tor',
        'location_of_tor',
        'area_office',
        'main_actions',
        'comments',
        "last_modified",
        "last_modified_by",
        ]
    title = "Filtered list of Maret Committees"
    sheet_title = "Committees"

    def val(obj, field):
        if "meeting_frequency_choices" in field:
            val = " --- "
            if obj.meeting_frequency_choices:
                val = obj.get_meeting_frequency_choices_display()
        elif "date_last_modified" in field:
            val = obj.last_modified.strftime("%Y-%m-%d")
        else:
            val = str(get_field_value(obj, field))
        return val


class OrganizationReportMixin:
    select_fk_fields = ["province", "last_modified_by"]
    field_list = [
        'id|Interaction Id',
        'name_eng',
        'former_name',
        'abbrev',
        'email',
        'address',
        'mailing_address',
        'city',
        'postal_code',
        'province',
        'phone',
        'fax',
        'grouping',
        'regions',
        'website',
        'category',
        'date_last_modified',
        'last_modified_by'
        ]
    title = "Filtered list of Maret Organizations"
    sheet_title = "Organizations"

    def val(obj, field):
        if "date_last_modified" in field:
            val = obj.date_last_modified.strftime("%Y-%m-%d")
        else:
            val = str(get_field_value(obj, field))
        return val


class PersonReportMixin:
    select_fk_fields = ["language", "last_modified_by"]
    field_list = [
        'id|Interaction Id',
        "designation",
        "first_name",
        "last_name",
        "phone_1",
        "phone_2",
        "email_1",
        "email_2",
        "cell",
        "fax",
        "language",
        "notes",
        "email_block",
        "date_last_modified",
        "last_modified_by",
        ]
    title = "Filtered list of Maret Contacts"
    sheet_title = "Contacts"

    def val(obj, field):
        if "date_last_modified" in field:
            val = obj.date_last_modified.strftime("%Y-%m-%d")
        else:
            val = str(get_field_value(obj, field))
        return val


def generate_maret_report(qs, mixin):
    qs = qs.select_related(*mixin.select_fk_fields)
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

    field_list = mixin.field_list

    # define the header
    header = [get_verbose_label(qs.first(), field) for field in field_list]
    title = mixin.title

    # define a worksheet
    my_ws = workbook.add_worksheet(name=mixin.sheet_title)
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    i = 3
    for obj in qs:
        j = 0
        for field in field_list:
            val = mixin.val(obj, field)
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

