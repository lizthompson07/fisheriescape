import statistics
import pandas
import unicodecsv as csv
import xlsxwriter as xlsxwriter
from django.http import HttpResponse
from django.template.defaultfilters import yesno
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
from . import models
import numpy as np
import os
import pandas as pd


def generate_master_spreadsheet(fiscal_year):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
    target_file = "temp_export.xlsx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    worksheet1 = workbook.add_worksheet(name="Project List")
    worksheet2 = workbook.add_worksheet(name="FTE List")

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'normal'})
    total_format = workbook.add_format({'bg_color': '#D6D1C0', "align": 'center'})
    normal_format = workbook.add_format({"align": 'normal'})
    bold_format = workbook.add_format({"align": 'center', 'bold': True})

    # spreadsheet: Project List #
    #############################

    # get a project list for the year
    project_list = models.Project.objects.filter(fiscal_year=fiscal_year)

    header = [
        'project_title',
        'section',
        'program',
        'budget_code',
        'status',
        'approved',
        'start_date',
        'end_date',
        'description',
        'priorities',
        'deliverables',
        'data_collection',
        'data_sharing',
        'data_storage',
        'metadata_url',
        'regional_dm',
        'regional_dm_needs',
        'sectional_dm',
        'sectional_dm_needs',
        'vehicle_needs',
        'it_needs',
        'chemical_needs',
        'ship_needs',
        'date_last_modified',
        'last_modified_by',
    ]

    worksheet1.write_row(0, 0, header, header_format)

    # for p in project_list:
    #     data_row = [
    #         s.station.site.site,
    #         s.station.station_number,
    #         s.station.name,
    #         s.start_date.strftime("%d/%m/%Y"),
    #         s.start_date.month,
    #         s.start_date.year,
    #     ]

    workbook.close()
    return target_url
