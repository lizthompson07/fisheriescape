import statistics
import pandas
import unicodecsv as csv
import xlsxwriter as xlsxwriter
from django.http import HttpResponse
from django.template.defaultfilters import yesno
from django.utils import timezone
from math import pi

from bokeh.io import show, export_png, export_svgs
from bokeh.models import SingleIntervalTicker, ColumnDataSource, HoverTool, LabelSet, Label, Title
from bokeh.plotting import figure, output_file, save
from bokeh import palettes
from bokeh.transform import cumsum
from django.db.models import Sum, Q
from shutil import rmtree
from django.conf import settings

from lib.functions.nz import nz
from lib.functions.verbose_field_name import verbose_field_name
from . import models
import numpy as np
import os
import pandas as pd


def generate_capacity_spreadsheet(fy=None, orgs=None):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'ihub', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'ihub', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'normal',
         "text_wrap": True})
    normal_format = workbook.add_format({"align": 'left', "text_wrap": True})

    # get an entry list for the fiscal year (if any)
    if fy:
        entry_list = models.Entry.objects.filter(fiscal_year=fy)
    else:
        entry_list = models.Entry.objects.all()

    # define the header
    header = [
        "Entry ID",
        verbose_field_name(entry_list.first(), 'title'),
        verbose_field_name(entry_list.first(), 'organization'),
        verbose_field_name(entry_list.first(), 'status'),
        verbose_field_name(entry_list.first(), 'sector'),
        verbose_field_name(entry_list.first(), 'entry_type'),
        verbose_field_name(entry_list.first(), 'initial_date'),
        verbose_field_name(entry_list.first(), 'leads'),
        verbose_field_name(entry_list.first(), 'region'),
        verbose_field_name(entry_list.first(), 'funding_needed'),
        verbose_field_name(entry_list.first(), 'funding_requested'),
        verbose_field_name(entry_list.first(), 'amount_expected'),
        verbose_field_name(entry_list.first(), 'transferred'),
        verbose_field_name(entry_list.first(), 'amount_transferred'),
        verbose_field_name(entry_list.first(), 'fiscal_year'),
        verbose_field_name(entry_list.first(), 'funding_purpose'),
        verbose_field_name(entry_list.first(), 'date_last_modified'),
        verbose_field_name(entry_list.first(), 'date_created'),
        verbose_field_name(entry_list.first(), 'last_modified_by'),
        verbose_field_name(entry_list.first(), 'created_by'),
    ]

    # worksheets #
    ##############

    # each org should be represented on a separate worksheet
    # therefore determine an appropriate org list
    if orgs:
        org_list = [models.Organization.objects.get(pk=int(o)) for o in orgs.split(",")]
    else:
        org_list = models.Organization.objects.all()

    for org in org_list:
        if org.entries.count() > 0:
            my_ws = workbook.add_worksheet(name=org.abbrev)

            # create the col_max column to store the length of each header
            # should be a maximum column width to 100
            col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
            my_ws.write_row(0, 0, header, header_format)

            i = 1
            for e in entry_list.filter(organization=org):

                data_row = [
                    e.id,
                    e.title,
                    str(e.organization),
                    str(e.status),
                    str(e.sector),
                    str(e.entry_type),
                    e.initial_date.strftime("%Y-%m-%d"),
                    e.leads,
                    str(e.region),
                    e.funding_needed,
                    e.funding_requested,
                    e.amount_expected,
                    e.transferred,
                    e.amount_transferred,
                    e.fiscal_year,
                    nz(str(e.funding_purpose), ""),
                    e.date_created.strftime("%Y-%m-%d"),
                    "{} {}".format(e.created_by.first_name, e.created_by.last_name),
                    e.date_last_modified.strftime("%Y-%m-%d"),
                    "{} {}".format(e.last_modified_by.first_name, e.last_modified_by.last_name),
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

                my_ws.write_row(i, 0, data_row, normal_format)
                i += 1

            for j in range(0, len(col_max)):
                my_ws.set_column(j, j, width=col_max[j] * 1.1)

            num_row = entry_list.filter(organization=org).count()+10

            # set formatting for status
            for status in models.Status.objects.all():
                my_ws.conditional_format(0, 3, num_row, 3,
                                         {
                                             'type': 'cell',
                                             'criteria': 'equal to',
                                             'value': '"{}"'.format(status.name),
                                             'format': workbook.add_format({'bg_color': status.color, }),
                                         })

            # set formatting for entry type
            for entry_type in models.EntryType.objects.all():
                my_ws.conditional_format(0, 5, num_row, 5,
                                         {
                                             'type': 'cell',
                                             'criteria': 'equal to',
                                             'value': '"{}"'.format(entry_type.name),
                                             'format': workbook.add_format({'bg_color': entry_type.color, }),
                                         })


    workbook.close()
    return target_url
