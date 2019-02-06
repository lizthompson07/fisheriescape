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


def generate_species_sample_spreadsheet(species_list=None):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'grais', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'grais', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'normal',
         "text_wrap": True})
    normal_format = workbook.add_format({"align": 'left', "text_wrap": True})
    # Add a format. Light red fill with dark red text.
    red_format = workbook.add_format({'bg_color': '#FFC7CE',
                                      'font_color': '#9C0006'})

    # Add a format. Green fill with dark green text.
    green_format = workbook.add_format({'bg_color': '#C6EFCE',
                                        'font_color': '#006100'})

    # get a sample instance to create header
    my_sample = models.Sample.objects.first()
    my_species = models.Species.objects.first()

    # define the header
    header = [
        "Species ID",
        verbose_field_name(my_species, 'common_name'),
        verbose_field_name(my_species, 'scientific_name'),
        verbose_field_name(my_species, 'abbrev'),
        verbose_field_name(my_species, 'epibiont_type'),
        verbose_field_name(my_species, 'tsn'),
        verbose_field_name(my_species, 'aphia_id'),
        "Sample ID",
        "Observation platform",
        "Observation year",
        "Observation month",
        "Observation day",
        verbose_field_name(my_sample, 'station'),
        verbose_field_name(my_sample.station, 'province'),
        verbose_field_name(my_sample.station, 'latitude_n'),
        verbose_field_name(my_sample.station, 'longitude_w'),
        "observed at station?",
        "observed on line?",
        "observed on collector surface?",
        "% surface coverage (sample average)?",
    ]

    # worksheets #
    ##############
    new_species_list = [models.Species.objects.get(pk=int(s)) for s in species_list.split(",")]
    i = 1
    my_ws = workbook.add_worksheet(name="Samples")
    for species in new_species_list:

        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
        my_ws.write_row(0, 0, header, header_format)

        # get a list of samples for each requested species FROM ALL SOURCES
        sample_list = [models.Sample.objects.get(pk=s["surface__line__sample"]) for s in
                       models.SurfaceSpecies.objects.filter(species=species).values(
                           "surface__line__sample").distinct()]
        sample_list.extend(
            [models.Sample.objects.get(pk=s["sample"]) for s in
             models.SampleSpecies.objects.filter(species=species).values(
                 "sample").distinct()]
        )
        sample_list.extend(
            [models.Sample.objects.get(pk=s["line__sample"]) for s in
             models.LineSpecies.objects.filter(species=species).values(
                 "line__sample").distinct()]
        )
        # distill the list
        sample_set = set(sample_list)

        for sample in sample_set:
            if sample.date_retrieved:
                obs_year = sample.date_retrieved.year
                obs_month = sample.date_retrieved.month
                obs_day = sample.date_retrieved.day
            else:
                obs_year = None
                obs_month = None
                obs_day = None

            if models.SampleSpecies.objects.filter(sample=sample, species=species).count() > 0:
                at_station = "yes"
            else:
                at_station = "no"

            if models.LineSpecies.objects.filter(line__sample=sample, species=species).count() > 0:
                on_line = "yes"
            else:
                on_line = "no"

            if models.SurfaceSpecies.objects.filter(surface__line__sample=sample, species=species).count() > 0:
                on_surface = "yes"
            else:
                on_surface = "no"

            # calculate the % coverage
            if on_surface:
                # for each surface, determine the percent coverage and store in list
                ## only look at plates
                coverage_list = []
                for surface in models.Surface.objects.filter(line__sample=sample).filter(surface_type="pl"):
                    try:
                        my_coverage = models.SurfaceSpecies.objects.get(surface=surface, species=species).percent_coverage
                    except:
                        my_coverage = 0
                    coverage_list.append(my_coverage)
                mean_coverage = statistics.mean(coverage_list)

            else:
                mean_coverage = "n/a"

            data_row = [
                species.id,
                species.common_name,
                species.scientific_name,
                species.abbrev,
                species.get_epibiont_type_display(),
                species.tsn,
                species.aphia_id,
                sample.id,
                'Biofouling Monitoring',
                obs_year,
                obs_month,
                obs_day,
                sample.station.station_name,
                sample.station.province.abbrev,
                sample.station.latitude_n,
                sample.station.longitude_w,
                at_station,
                on_line,
                on_surface,
                mean_coverage,
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

        # set formatting for last three columns
        my_ws.conditional_format(0, header.index("observed at station?"), i,
                                 header.index("observed on collector surface?"),
                                 {
                                     'type': 'cell',
                                     'criteria': 'equal to',
                                     'value': '"yes"',
                                     'format': green_format,
                                 })
        my_ws.conditional_format(0, header.index("observed at station?"), i,
                                 header.index("observed on collector surface?"),
                                 {
                                     'type': 'cell',
                                     'criteria': 'equal to',
                                     'value': '"no"',
                                     'format': red_format,
                                 })

    workbook.close()
    return target_url
