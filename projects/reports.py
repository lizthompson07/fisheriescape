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

def generate_annual_watershed_spreadsheet(site, year):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'camp', 'temp')
    target_file = "temp_data_export.xlsx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'camp', 'temp', target_file)

    # get a sample list for the site / year
    sample_list = models.Sample.objects.filter(year=year).filter(station__site=site).order_by("start_date",
                                                                                              "station__station_number")
    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)
    worksheet1 = workbook.add_worksheet(name="Fauna - Faune")
    worksheet2 = workbook.add_worksheet(name="Sediment - Sédiment")
    worksheet3 = workbook.add_worksheet(name="Vegetation - Végétation")

    # spreadsheet: Fauna #
    ######################

    # get a list of species obs for which sav == false
    species_list = models.Species.objects.filter(sav=False).order_by("code")

    # convert species list into headers (a, yoy, tot)
    species_header_list = []
    for s in species_list:
        species_header_list.append("{}(A)".format(s.code))
        species_header_list.append("{}(YOY)".format(s.code))
        species_header_list.append("{}(TOT)".format(s.code))

    header_eng = [
        "Site location",
        "Station #",
        "Station name",
        "Date",
        "Month",
        "Year",
        "Time start",
        "Time finish",
        "Water Sample #",
        "Rain 24h Y / N",
        "Stage of tide",
        "Samplers name",
        "Water temp",
        "Salinity",
        "Dissolved Oxygen",
        "Water turbidity",
        "SP. RICHNESS",
        "TOTAL",
    ]

    header_fre = [
        "Location Site",
        "# Station",
        "Nom station",
        "(dj/mm/ya)",
        "Mois",
        "Année",
        "Heure début",
        "Heure fin",
        "# échantillon d'eau",
        "Pluie 24h O / N",
        "Stade de marée",
        "Nom échantillonneurs",
        "Temp eau",
        "Salinité",
        "Oxygène dissout",
        "Turbidité de l'eau",
        "SP. RICHNESS",
        "TOTAL",
    ]

    # insert species headers 2 from the last item in header_eng / fre
    header_eng[-2:-2] = species_header_list
    header_fre[-2:-2] = species_header_list

    # prime a dataframe obj with the two headers
    my_df = pandas.DataFrame([header_eng, header_fre], columns=[i for i in range(0, len(header_eng))])

    # write some data
    for s in sample_list:
        data_row = [
            s.station.site.site,
            s.station.station_number,
            s.station.name,
            s.start_date.strftime("%d/%m/%Y"),
            s.start_date.month,
            s.start_date.year,
            s.start_date.strftime("%H:%M"),
            s.end_date.strftime("%H:%M"),
            s.nutrient_sample_id,
            yesno(s.rain_past_24_hours),
            "{} - {}".format(s.get_tide_state_display(), s.get_tide_direction_display(), ),
            s.samplers,
            s.h2o_temperature_c,
            s.salinity,
            s.dissolved_o2,
            s.get_water_turbidity_display(),
        ]

        # now get species data
        species_obs_list = []

        for species in species_list:
            try:
                species_obs = models.SpeciesObservation.objects.get(sample=s, species=species)
            except:
                species_obs_list.append(0)
                species_obs_list.append(0)
                species_obs_list.append(0)
            else:
                nz(species_obs_list.append(species_obs.adults), 0)
                nz(species_obs_list.append(species_obs.yoy), 0)
                species_obs_list.append(species_obs.total_non_sav)

        data_row.extend(species_obs_list)

        # species richness
        annual_obs = models.SpeciesObservation.objects.filter(sample=s, species__sav=False).values(
            'species_id',
        ).distinct()
        species_set = set([i["species_id"] for i in annual_obs])
        data_row.append(len(species_set))

        # total count
        total = models.SpeciesObservation.objects.filter(sample=s).filter(species__sav=False).values(
            'sample_id'
        ).distinct().annotate(dsum=Sum('total_non_sav'))
        data_row.append(total[0]['dsum'])

        # store data_row in a dataframe
        my_df = my_df.append(pandas.DataFrame([data_row, ], columns=[i for i in range(0, len(data_row))]),
                             ignore_index=True)

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'center'})
    total_format = workbook.add_format({'bg_color': '#D6D1C0', "align": 'center'})
    normal_format = workbook.add_format({"align": 'center'})
    bold_format = workbook.add_format({"align": 'center', 'bold': True})

    # write dataframe to xlsx
    for i in range(0, my_df.shape[0]):
        for j in range(0, my_df.shape[1]):

            # tricky code since j and i are reverses from an intuitive perspective (i.e. not i,j)
            my_val = my_df[j][i]

            if i <= 1:
                worksheet1.write(i, j, my_val, header_format)
            elif "(TOT)" in my_df[j][0]:
                worksheet1.write(i, j, my_val, total_format)
            else:
                worksheet1.write(i, j, my_val, normal_format)

    # add the total at bottom right
    total_sum = 0
    count = 0
    for j in my_df[my_df.shape[1] - 1]:
        if count > 1:
            total_sum = total_sum + j
        count += 1
    worksheet1.write(my_df.shape[0], my_df.shape[1] - 2, "TOTAL", bold_format)
    worksheet1.write(my_df.shape[0], my_df.shape[1] - 1, total_sum, bold_format)

    # adjust the width of the columns based on the max string length in each col
    col_max = [max([len(str(s)) for s in my_df[j].values]) for j in my_df.columns]
    for j in my_df.columns:
        worksheet1.set_column(j, j, width=col_max[j] * 1.1)

    # spreadsheet: sediment #
    #########################

    # get a list of species obs for which sav == false
    species_list = models.Species.objects.filter(sav=False).order_by("code")

    for s in species_list:
        species_header_list.append("{}(A)".format(s.code))
        species_header_list.append("{}(YOY)".format(s.code))
        species_header_list.append("{}(TOT)".format(s.code))

    header_eng = [
        "Site location",
        "Station #",
        "Station name",
        "Date",
        "Month",
        "Year",
        "% sand",
        "% gravel",
        "% rocky",
        "% mud",
        "Overall visual sediment observation",
    ]

    header_fre = [
        "Location Site",
        "# Station",
        "Nom station",
        "(dj/mm/ya)",
        "Mois",
        "Année",
        "% sable",
        "% gravier",
        "% rocheux",
        "% vase",
        "Observation visuelle du sédiment",
    ]

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'center'})
    normal_format = workbook.add_format({"align": 'center'})

    # prime a dataframe obj with the two headers
    my_df = pandas.DataFrame([header_eng, header_fre], columns=[i for i in range(0, len(header_eng))])

    # write some data
    for s in sample_list:
        data_row = [
            s.station.site.site,
            s.station.station_number,
            s.station.name,
            s.start_date.strftime("%d/%m/%Y"),
            s.start_date.month,
            s.start_date.year,
            "{}%".format(nz(s.percent_sand, 0)),
            "{}%".format(nz(s.percent_gravel, 0)),
            "{}%".format(nz(s.percent_rock, 0)),
            "{}%".format(nz(s.percent_mud, 0)),
            "{}%".format(
                sum([nz(s.percent_sand, 0), nz(s.percent_gravel, 0), nz(s.percent_rock, 0), nz(s.percent_mud, 0)])),
        ]

        # store data_row in a dataframe
        my_df = my_df.append(pandas.DataFrame([data_row, ], columns=[i for i in range(0, len(data_row))]),
                             ignore_index=True)

    # write dataframe to xlsx
    for i in range(0, my_df.shape[0]):
        for j in range(0, my_df.shape[1]):

            # tricky code since j and i are reverses from an intuitive perspective (i.e. not i,j)
            my_val = my_df[j][i]

            if i <= 1:
                worksheet2.write(i, j, my_val, header_format)
            else:
                worksheet2.write(i, j, my_val, normal_format)

    # adjust the width of the columns based on the max string length in each col
    col_max = [max([len(str(s)) for s in my_df[j].values]) for j in my_df.columns]
    for j in my_df.columns:
        worksheet2.set_column(j, j, width=col_max[j] * 1.1)

    # spreadsheet: Veg #
    ####################

    # get a list of species obs for which sav == true
    species_list = models.Species.objects.filter(sav=True).order_by("code")

    # convert sav species list into headers (a, yoy, tot)
    species_header_list_eng = [s.common_name_eng for s in species_list]
    species_header_list_fre = [s.common_name_fre for s in species_list]

    header_eng = [
        "Site location",
        "Station #",
        "Station name",
        "Date",
        "Month",
        "Year",
    ]

    header_fre = [
        "Location Site",
        "# Station",
        "Nom station",
        "(dj/mm/ya)",
        "Mois",
        "Année",
    ]

    # insert species headers 2 from the last item in header_eng / fre
    header_eng.extend(species_header_list_eng)
    header_fre.extend(species_header_list_fre)

    # prime a dataframe obj with the two headers
    my_df = pandas.DataFrame([header_eng, header_fre], columns=[i for i in range(0, len(header_eng))])

    # write some data
    for s in sample_list:
        data_row = [
            s.station.site.site,
            s.station.station_number,
            s.station.name,
            s.start_date.strftime("%d/%m/%Y"),
            s.start_date.month,
            s.start_date.year,
        ]

        # now get species data
        species_obs_list = []

        for species in species_list:
            try:
                species_obs = models.SpeciesObservation.objects.get(sample=s, species=species)
            except:
                species_obs_list.append(0)
            else:
                species_obs_list.append(nz(species_obs.total_sav, 0))

        data_row.extend(species_obs_list)

        # store data_row in a dataframe
        my_df = my_df.append(pandas.DataFrame([data_row, ], columns=[i for i in range(0, len(data_row))]),
                             ignore_index=True)

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'center'})
    normal_format = workbook.add_format({"align": 'center'})

    # write dataframe to xlsx
    for i in range(0, my_df.shape[0]):
        for j in range(0, my_df.shape[1]):

            # tricky code since j and i are reverses from an intuitive perspective (i.e. not i,j)
            my_val = my_df[j][i]

            if i <= 1:
                worksheet3.write(i, j, my_val, header_format)
            else:
                worksheet3.write(i, j, my_val, normal_format)

    # adjust the width of the columns based on the max string length in each col
    col_max = [max([len(str(s)) for s in my_df[j].values]) for j in my_df.columns]
    for j in my_df.columns:
        worksheet3.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url
