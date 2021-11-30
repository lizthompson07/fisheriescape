import os

import xlsxwriter
from bs4 import BeautifulSoup
from django.conf import settings
from django.template import loader
from django.utils import timezone
from django.utils.translation import gettext as _
from docx import Document
from html2text import html2text
from htmldocx import HtmlToDocx
from textile import textile

from dm_apps.context_processor import my_envr
from lib.templatetags.verbose_names import get_verbose_label, get_field_value
from res import models


def get_application_context(application, request):
    context = dict(object=application)
    qs1 = models.SiteSection.objects.filter(section=1)
    if qs1.exists():
        context["annex_a_text"] = qs1.first().description_html
    qs2 = models.SiteSection.objects.filter(section=2)
    if qs2.exists():
        context["annex_b_text"] = qs2.first().description_html

    context["contexts"] = models.Context.objects.all()
    context["basic_fields"] = [
        "fiscal_year",
        "status",
        "applicant",
        "manager",
        "dates|{}".format(_("dates")),
        "section",
        "current_group_level",
        "target_group_level",
        "current_position_title",
        "work_location",
        "last_application",
        "last_promotion",
        "academic_background_html",
        "employment_history_html",
    ]
    context["recommendation_fields"] = [
        "recommendation_text_html",
        "decision",
        "manager_signature|{}".format(_("manager signature")),
        "applicant_signature|{}".format(_("applicant signature")),
        "applicant_comment",
    ]
    context["section_2_fields"] = [
        "objectives_html",
        "relevant_factors_html",
    ]
    context.update(my_envr(request))
    return context


def generate_word_application(application, request):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_export.docx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)
    document = Document()
    t = loader.get_template('res/application_print/main_word.html')
    context = get_application_context(application, request)
    rendered = t.render(context)
    new_parser = HtmlToDocx()
    new_parser.add_html_to_document(rendered, document)

    document.save(target_file_path)
    return target_url


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
    title = "res Dive Log"

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
