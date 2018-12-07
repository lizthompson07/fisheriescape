from bokeh.plotting import figure, output_file, save
from bokeh import palettes
from django.db.models import Sum, Count
from shutil import rmtree
from . import models

import numpy as np
import os


def generate_species_count_report(species_list):
    # start assigning files and by cleaning the temp dir
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, 'templates', 'camp', 'temp')
    target_file = os.path.join(target_dir, 'report_temp.html')

    try:
        rmtree(target_dir)
    except:
        print("no such dir.")
    os.mkdir(target_dir)

    # output to static HTML file
    output_file(target_file)

    # create a new plot
    p = figure(
        title="Count of Species Observations by Year",
        tools="pan,box_zoom,wheel_zoom,reset,save",
        x_axis_label='Year',
        y_axis_label='Count',
        plot_width=1200, plot_height=600,

    )

    # determine number of species
    # print(species_list)
    my_list = species_list.split(",")

    # prime counter variable
    i = 0

    # generate color palette
    if len(my_list) <= 9:
        colors = palettes.Set1[len(my_list)]
    else:
        colors = palettes.Category20[len(my_list)]

    for obj in my_list:
        sp_id = int(obj.replace("'", ""))
        # create a new file containing data
        qs = models.SpeciesObservation.objects.filter(species=sp_id).values(
            'sample__year'
        ).distinct().annotate(dsum=Sum('total_non_sav'))

        years = [i["sample__year"] for i in qs]
        counts = [i["dsum"] for i in qs]
        my_sp = models.Species.objects.get(pk=sp_id)
        legend_title = "Annual observations for {}".format(my_sp.common_name_eng)
        p.line(years, counts, legend=legend_title, line_color=colors[i], line_width=3)
        p.circle(years, counts, legend=legend_title, fill_color=colors[i], line_color=colors[i], size=8)
        i += 1

    save(p)


def generate_species_richness_report(site=None):
    # start assigning files and by cleaning the temp dir
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, 'templates', 'camp', 'temp')
    target_file = os.path.join(target_dir, 'report_temp.html')

    try:
        rmtree(target_dir)
    except:
        print("no such dir.")
    os.mkdir(target_dir)

    # output to static HTML file
    output_file(target_file)

    # create a new plot
    p = figure(
        title="Count of Species Observations by Year",
        tools="pan,box_zoom,wheel_zoom,reset,save",
        x_axis_label='Year',
        y_axis_label='Species count',
        plot_width=1200, plot_height=800,
        x_axis_type="linear"

    )
    p.grid.grid_line_alpha = 1

    if site:
        # reset title
        p.title.text = "Count of Species Observations by Year - {}".format(models.Site.objects.get(pk=site))

        # first we need a list of stations
        stations = models.Station.objects.filter(site_id=site).order_by("name")

        # generate color palette
        if len(stations) <= 9:
            colors = palettes.Set1[len(stations)]
        else:
            colors = palettes.Category20[len(stations)]

        i = 0
        for station in stations:
            print(station)
            qs_years = models.Sample.objects.filter(station=station).order_by("year").values(
                'year',
            ).distinct()

            years = []
            counts = []

            for obj in qs_years:
                y = obj['year']
                annual_obs = models.SpeciesObservation.objects.filter(sample__year=y, sample__station=station,
                                                                      species__sav=False).values(
                    'species_id',
                ).distinct()
                species_set = set([i["species_id"] for i in annual_obs])
                years.append(y)
                counts.append(len(species_set))

            legend_title = str(station)
            p.line(years, counts, legend=legend_title, line_width=1, line_color=colors[i])  # , line_dash="4 4"
            p.circle(years, counts, legend=legend_title, fill_color=colors[i], line_color=colors[i], size=3)
            i += 1

        # Show a line for entire site
        qs_years = models.Sample.objects.filter(station__site_id=site).order_by("year").values(
            'year',
        ).distinct()

        years = []
        counts = []

        for obj in qs_years:
            y = obj['year']
            annual_obs = models.SpeciesObservation.objects.filter(sample__year=y, sample__station__site_id=site,
                                                                  species__sav=False).values(
                'species_id',
            ).distinct()
            species_set = set([i["species_id"] for i in annual_obs])
            years.append(y)
            counts.append(len(species_set))

        legend_title = "Entire site"
        p.line(years, counts, legend=legend_title, line_width=3, line_color='black')
        p.circle(years, counts, legend=legend_title, fill_color='black', line_color='black', size=8)
        # TODO: should we show the number of stations visited?


    else:
        qs_years = models.Sample.objects.all().order_by("year").values(
            'year',
        ).distinct()

        years = []
        counts = []

        for obj in qs_years:
            y = obj['year']
            annual_obs = models.SpeciesObservation.objects.filter(sample__year=y, species__sav=False).values(
                'species_id',
            ).distinct()
            species_set = set([i["species_id"] for i in annual_obs])
            years.append(y)
            print(years)
            counts.append(len(species_set))
            print(counts)
        # my_sp = models.Species.objects.get(pk=sp_id)
        legend_title = "All stations"
        p.line(years, counts, legend=legend_title, line_width=3)
        p.circle(years, counts, legend=legend_title, fill_color='white', size=8)
        # TODO: should we show the number of stations visited?

    save(p)
