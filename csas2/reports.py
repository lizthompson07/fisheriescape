import os
from io import BytesIO
import xlsxwriter
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
        TAG_LEAD_REGION=tor.process.lead_region.tname,
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


def generate_meeting_report(fiscal_year=None, is_posted=None):
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

    # get the meeting list
    objects = models.Meeting.objects.filter(is_planning=False)
    if fiscal_year:
        objects = objects.filter(process__fiscal_year=fiscal_year)

    if is_posted is not None:
        objects = objects.filter(process__is_posted=is_posted)

    field_list = [
        'process.fiscal_year|fiscal year',
        'process.is_posted|Has been posted?',
        'process.name|Process name',
        'process.scope_type|type of process',
        'tor_display_dates|meeting dates',
        'process.name|meeting name (English)',
        'process.nom|meeting name (French)',
        'chair|Chairperson name',
        'process.coordinator|CSAS Coordinator',
        'process.advisors|Science advisors',
        'expected publications',
        'other regions',
    ]

    # define the header
    header = [get_verbose_label(objects.first(), field) for field in field_list]
    title = "CSAS Meeting Report"

    # define a worksheet
    my_ws = workbook.add_worksheet(name="meeting report")
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    i = 3
    for obj in objects:
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
        j = 0
        for field in field_list:

            if "other regions" in field:
                my_val = listrify(obj.process.other_regions.all())
                my_ws.write(i, j, my_val, normal_format)
            elif "advisors" in field:
                my_val = listrify(obj.process.advisors.all())
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


def generate_request_list(requests):
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
        'id',
        'fiscal_year',
        'title|{}'.format(_("title")),
        'status',
        'has_process|{}'.format(_("has process?")),
        'coordinator',
        'client',
        'region|{}'.format(_("region")),
        'sector|{}'.format(_("sector")),
        'section|{}'.format(_("section")),
    ]

    # define the header
    header = [get_verbose_label(requests.first(), field) for field in field_list]
    title = "CSAS Request List"

    # define a worksheet
    my_ws = workbook.add_worksheet(name="requests")
    my_ws.write(0, 0, title, title_format)
    my_ws.write_row(2, 0, header, header_format)

    i = 3
    for obj in requests:
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
        j = 0
        for field in field_list:

            if "other regions" in field:
                my_val = listrify(obj.process.other_regions.all())
                my_ws.write(i, j, my_val, normal_format)
            elif "advisors" in field:
                my_val = listrify(obj.process.advisors.all())
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
