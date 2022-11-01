import os

import xlsxwriter
from django.conf import settings
from django.utils import timezone

from lib.templatetags.verbose_names import get_verbose_label, get_field_value


class ReportLoader:
    def __init__(self):
        self.field_list = []
        self.select_fk_fields = []
        self.title = ""
        self.sheet_title = ""

    def val(self, obj, field):
        out_val = obj[field]
        return out_val


class InteractionReport:
    def __init__(self):
        self.select_fk_fields = ["committee", "branch", "area_office", "area_office_program", "division", "lead_region",
                                 "lead_national_sector", "last_modified_by"]
        self.field_list = [
            'id|Interaction Id',
            'description',
            'interaction_type',
            'is_committee',
            'committee',
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
            'other_dfo_areas',
            'other_dfo_regions',
            'dfo_national_sectors',
            'dfo_role',
            'external_organization',
            'external_contact',
            'dfo_liaison',
            'other_dfo_participants',
            'action_items',
            'comments',
            'last_modified',
            'last_modified_by',
            ]
        self.title = "Filtered list of Maret Interactions"
        self.sheet_title = "Interactions"

    def val(self, obj, field):
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


class CommitteeReport:
    def __init__(self):
        self.select_fk_fields = ["branch", "division", "area_office", "area_office_program", "division", "lead_region",
                                 "lead_national_sector", "last_modified_by"]
        self.field_list = [
            'id|Committee Id',
            'name',
            'main_topic',
            'species',
            'lead_region',
            'lead_national_sector',
            'branch',
            'division',
            'area_office',
            'area_office_program',
            'other_dfo_branch',
            'other_dfo_areas',
            'other_dfo_regions',
            'dfo_national_sectors',
            'dfo_role',
            'is_dfo_chair',
            'external_chair',
            'external_contact',
            'external_organization',
            'dfo_liaison',
            'other_dfo_participants',
            'first_nation_participation',
            'municipal_participation',
            'provincial_participation',
            'other_federal_participation',
            'meeting_frequency',
            'are_tor',
            'location_of_tor',
            'main_actions',
            'comments',
            'committee_interactions|Interaction(s)',
            "last_modified",
            "last_modified_by",
            ]
        self.title = "Filtered list of Maret Committees"
        self.sheet_title = "Committees"

    def val(self, obj, field):
        if "meeting_frequency_choices" in field:
            val = " --- "
            if obj.meeting_frequency_choices:
                val = obj.get_meeting_frequency_choices_display()
        elif "date_last_modified" in field:
            val = obj.last_modified.strftime("%Y-%m-%d")
        elif "committee_interactions" in field:
            val = " --- "
            if obj.committee_interactions.first():
                val = ", ".join([inter.__str__() for inter in obj.committee_interactions.all()])
        else:
            val = str(get_field_value(obj, field))
        return val


class OrganizationReport:
    def __init__(self):
        self.select_fk_fields = ["province", "last_modified_by"]
        self.field_list = [
            'id|Organization Id',
            'name_eng',
            'ext_org__category|Category',
            'grouping',
            'abbrev',
            'ext_org__email|Email',
            'address',
            'mailing_address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
            'notes',
            'ext_org__area|Area(s)',
            'regions',
            'ext_org__associated_provinces|Associated Provinces',
            'organization_committees|Committees/Working groups(s)',
            'former_name',
            'website',
            'organization_members|Member(s)',
            'organization_interactions|Interaction(s)',
            'date_last_modified',
            'last_modified_by'
            ]
        self.title = "Filtered list of Maret Organizations"
        self.sheet_title = "Organizations"

    def val(self, obj, field):
        val = " --- "
        if "date_last_modified" in field:
            val = obj.date_last_modified.strftime("%Y-%m-%d")
        elif "organization_members" in field:
            if obj.members.first():
                val = ", ".join([member.person.full_name for member in obj.members.all()])
        elif "organization_interactions" in field:
            if obj.interaction_ext_organization.first():
                val = ", ".join([inter.__str__() for inter in obj.interaction_ext_organization.all()])
        elif "organization_committees" in field:
            if obj.committee_ext_organization.first():
                val = ", ".join([committee.__str__() for committee in obj.committee_ext_organization.all()])
        elif "ext_org__" in field:
            if obj.ext_org.first():
                # replace this with field.removeprefix once python 3.9 hits.
                ext_org_field = field[len("ext_org__"):]
                val = str(get_field_value(obj.ext_org.first(), ext_org_field))
        else:
            val = str(get_field_value(obj, field))
        return val


class PersonReport:
    def __init__(self):
        self.select_fk_fields = ["language", "last_modified_by"]
        self.field_list = [
            'id|Contact Id',
            "designation",
            "first_name",
            "last_name",
            "phone_1",
            "phone_2",
            "cell",
            "email_1",
            "email_2",
            "fax",
            "language",
            "notes",
            "committee|Committees / Working Groups",
            "email_block",
            "ogranizations | Organization Memberships",
            "interactions | Interactions",
            "date_last_modified",
            "last_modified_by",
            ]
        self.title = "Filtered list of Maret Contacts"
        self.sheet_title = "Contacts"

    def val(self, obj, field):
        val = " --- "
        if "date_last_modified" in field:
            val = obj.date_last_modified.strftime("%Y-%m-%d")
        elif "ogranizations" in field:
            if obj.memberships.first():
                val = ", ".join([membership.organization.__str__() for membership in obj.memberships.all()])
        elif "interactions" in field:
            if obj.interaction_ext_contact.first():
                val = ", ".join([interaction.__str__() for interaction in obj.interaction_ext_contact.all()])
        elif "committee" in field:
            if obj.committee_ext_contact.first():
                val = ", ".join(
                    [committee.__str__() for committee in obj.committee_ext_contact.all()])
        else:
            val = str(get_field_value(obj, field))
        return val


def generate_maret_report(qs, report_loader):
    report_class = report_loader()
    qs = qs.select_related(*report_class.select_fk_fields)
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

    field_list = report_class.field_list

    # define the header
    header = [get_verbose_label(qs.first(), field) for field in field_list]
    title = report_class.title

    # define a worksheet
    my_ws = workbook.add_worksheet(name=report_class.sheet_title)
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    i = 3
    for obj in qs:
        j = 0
        for field in field_list:
            val = report_class.val(obj, field)
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

