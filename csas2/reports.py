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


def generate_tor(tor, lang):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_export.docx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)

    if lang == "fr":
        template_file_path = os.path.join(settings.BASE_DIR, 'csas2', 'static', "csas2", "tor_template_fr.docx")
    else:
        template_file_path = os.path.join(settings.BASE_DIR, 'csas2', 'static', "csas2", "tor_template_en.docx")

    with open(template_file_path, 'rb') as f:
        source_stream = BytesIO(f.read())
    document = Document(source_stream)
    source_stream.close()

    activate(lang)
    dates = location = chair = "no meeting selected in terms of reference".upper()
    if tor.meeting:
        dates = tor.meeting.tor_display_dates
        if tor.meeting.is_virtual:
            location = _("Virtual Meeting")
        else:
            location = tor.meeting.location if tor.meeting.location else "TBD"
        chair = tor.meeting.chair if tor.meeting.chair else "TBD"

    expected_publications = ""
    for t in tor.expected_document_types.all():
        expected_publications += f"- {t}\n"

    field_dict = dict(
        TAG_TITLE=tor.process.tname,
        TAG_TYPE_SCOPE=tor.process.scope_type,
        TAG_LEAD_REGION=tor.process.lead_office.region.tname,
        TAG_DATES=dates,
        TAG_LOCATION=location,
        TAG_CHAIR=chair,
        TAG_CONTEXT=tor.context_fr if lang == "fr" else tor.context_en,
        TAG_OBJECTIVES=tor.objectives_fr if lang == "fr" else tor.objectives_en,
        TAG_EXPECTED_PUBLICATIONS=expected_publications,
        TAG_PARTICIPATION=tor.participation_fr if lang == "fr" else tor.participation_en,
        TAG_REFERENCES=tor.references_fr if lang == "fr" else tor.references_en,
    )
    for p in document.paragraphs:
        inline = p.runs
        for i in range(len(inline)):
            text = inline[i].text
            if text in field_dict.keys():
                text = text.replace(text, field_dict[text])
                inline[i].text = text

    document.save(target_file_path)
    deactivate()
    return target_url


def generate_meeting_report(meetings, site_url):
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

    field_list = [
        'process.fiscal_year|fiscal year',
        'process.is_posted|Has been posted?',
        'process.name|Process name',
        'process.status|Process status',
        'process.scope|Process scope',
        'process.type|Process type',
        'quarter|meeting quarter',
        'tor_display_dates|meeting dates',
        'process.name|meeting title (English)',
        'process.nom|meeting title (French)',
        'chair|Chairperson name',
        'process.coordinator|CSAS Coordinator',
        'process.advisors|Science advisors',
        'expected publications',
        'lead office',
        'other offices',
        'process.id|process ID',
        'client_regions|{}'.format(_("client regions")),
        'client_sectors|{}'.format(_("client sectors")),
        'client_sections|{}'.format(_("client sections")),
        'process.formatted_notes|{}'.format(_("process notes")),
    ]

    # define the header
    header = [get_verbose_label(meetings.first(), field) for field in field_list]
    title = "CSAS Meeting Report"

    # define a worksheet
    my_ws = workbook.add_worksheet(name="meeting report")
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    i = 3
    for obj in meetings:
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
        j = 0
        for field in field_list:

            if "other offices" in field:
                my_val = listrify(obj.process.other_offices.all())
                my_ws.write(i, j, my_val, normal_format)
            elif "lead office" in field:
                my_val = str(obj.process.lead_office)
                my_ws.write(i, j, my_val, normal_format)
            elif "scope" in field:
                my_val = str(obj.process.get_scope_display())
                my_ws.write(i, j, my_val, normal_format)
            elif "process.type" in field:
                my_val = str(obj.process.get_type_display())
                my_ws.write(i, j, my_val, normal_format)
            elif "status" in field:
                my_val = str(obj.process.get_status_display())
                my_ws.write(i, j, my_val, normal_format)
            elif "advisors" in field:
                my_val = listrify(obj.process.advisors.all())
                my_ws.write(i, j, my_val, normal_format)
            elif "sections" in field:
                my_val = obj.process.client_sections
                my_ws.write(i, j, my_val, normal_format)
            elif "sectors" in field:
                my_val = obj.process.client_sectors
                my_ws.write(i, j, my_val, normal_format)
            elif "regions" in field:
                my_val = obj.process.client_regions
                my_ws.write(i, j, my_val, normal_format)
            elif "expected publications" in field:
                if hasattr(obj.process, "tor"):
                    my_val = listrify(obj.process.tor.expected_document_types.all())
                else:
                    my_val = "n/a"
                my_ws.write(i, j, my_val, normal_format)
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


def generate_request_list(requests, site_url):
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
    date_format = workbook.add_format({'num_format': "mm/dd/yyyy", "align": 'left', 'border': 1, 'border_color': 'black', })

    field_list = [
        'id|{}'.format("CSAS Request ID"),
        'title',
        'translated_title',
        'fiscal_year',
        'advice_fiscal_year',
        'target_advice_date|{}'.format(_("advice date")),
        'status',
        'review.decision|{}'.format(_("recommendation")),
        'review.decision_text|{}'.format(_("recommendation explanation")),
        'has_process|{}'.format(_("has process?")),
        'coordinator',
        'client',
        'region|{}'.format(_("client region")),
        'sector|{}'.format(_("client sector")),
        'section|{}'.format(_("client section")),
    ]

    # define the header
    header = [get_verbose_label(requests.first(), field) for field in field_list]
    title = "CSAS Request List"

    # define a worksheet
    my_ws = workbook.add_worksheet(name="requests")
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    i = 3
    for obj in requests:
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        j = 0
        for field in field_list:

            if "other regions" in field:
                my_val = listrify(obj.process.other_regions.all())
                my_ws.write(i, j, my_val, normal_format)
            elif "advisors" in field:
                my_val = listrify(obj.process.advisors.all())
                my_ws.write(i, j, my_val, normal_format)
            elif "date" in field:
                my_val = obj.target_advice_date.strftime("%m/%d/%Y") if obj.target_advice_date else "---"
                my_ws.write(i, j, my_val, date_format)
            elif "decision|" in field:
                my_val = str(get_field_value(obj.review, "decision")) if hasattr(obj, "review") else "---"
                my_ws.write(i, j, my_val, normal_format)
            elif field == "title":
                my_val = str(get_field_value(obj, field))
                my_ws.write_url(i, j,
                                url=f'{site_url}/{reverse("csas2:request_detail", args=[obj.id])}',
                                string=f"{my_val}",
                                cell_format=hyperlink_format)
            elif "expected publications" in field:
                if hasattr(obj.process, "tor"):
                    my_val = listrify(obj.process.tor.expected_document_types.all())
                else:
                    my_val = "n/a"
                my_ws.write(i, j, my_val, normal_format)
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

def generate_process_list(processes, site_url):
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
    hyperlink_format = workbook.add_format({'border': 1, 'border_color': 'black', "font_color": "blue", "underline": True})

    field_list = [
        'id|{}'.format("CSAS Process ID"),
        'fiscal_year',
        'name',
        'nom',
        'scope_type|{}'.format(_("Advisory process type")),
        'status',
        'science_leads|{}'.format(_("Lead scientists")),
        'chair|{}'.format(_("chair")),
        'coordinator',
        'advisors',
        'lead_office',
        'other_offices',
        'expected_publications|{}'.format(_("expected publications")),
        'key_meetings|{}'.format(_("key meetings")),
        'doc_summary|{}'.format(_("document summary")),
        'formatted_notes|{}'.format(_("notes")),
    ]

    # define the header
    header = [get_verbose_label(processes.first(), field) for field in field_list]
    title = "CSAS Process List"

    # define a worksheet
    my_ws = workbook.add_worksheet(name="requests")
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]

    i = 3
    for obj in processes:
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        j = 0
        for field in field_list:

            if "other_regions" in field:
                my_val = listrify(obj.other_offices.all())
                my_ws.write(i, j, my_val, normal_format)
            elif "advisors" in field:
                my_val = listrify(obj.advisors.all())
                my_ws.write(i, j, my_val, normal_format)

            elif "expected publications" in field:
                if hasattr(obj, "tor"):
                    my_val = listrify(obj.tor.expected_document_types.all())
                else:
                    my_val = "n/a"
                my_ws.write(i, j, my_val, normal_format)
            elif field == "name":
                my_val = str(get_field_value(obj, field))
                my_ws.write_url(i, j,
                                url=f'{site_url}/{reverse("csas2:process_detail", args=[obj.id])}',
                                string=f"{my_val}",
                                cell_format=hyperlink_format)
            else:
                my_val = str(get_field_value(obj, field))
                my_ws.write(i, j, my_val, normal_format)

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            # if new value > stored value... replace stored value
            if len(str(my_val)) > col_max[j]:
                if len(str(my_val)) < 50:
                    col_max[j] = len(str(my_val))
                else:
                    col_max[j] = 50
            j += 1
        i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url
