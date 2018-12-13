import statistics

from math import pi

from bokeh.io import show, export_png, export_svgs
from bokeh.models import SingleIntervalTicker, ColumnDataSource, HoverTool, LabelSet, Label
from bokeh.plotting import figure, output_file, save
from bokeh import palettes
from bokeh.transform import cumsum
from django.db.models import Sum, Q
from shutil import rmtree
from django.conf import settings
from . import models
import numpy as np
import os
import pandas as pd


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
        tools="pan,box_zoom,wheel_zoom,reset,save,",
        # tooltips="@stations",
        x_axis_label='Year',
        y_axis_label='Species count',
        plot_width=1200, plot_height=800,
        x_axis_type="linear"

    )
    ticker = SingleIntervalTicker(interval=1)

    p.grid.grid_line_alpha = 1
    p.background_fill_color = None
    p.xaxis.minor_tick_line_color = None
    p.xaxis.ticker = ticker
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

            source = ColumnDataSource(data={
                'year': years,
                'count': counts,
                'station': list(np.repeat(str(station), len(years)))
            })

            p.line("year", "count", legend=legend_title, line_width=1, line_color=colors[i], source=source)
            # p.circle("year", "count", legend=legend_title, line_width=1, line_color=colors[i], source=source)
            p.circle("year", "count", legend=legend_title, fill_color=colors[i], line_color=colors[i], size=3,
                     source=source)

            p.add_tools(HoverTool(
                tooltips=[
                    ('year:', '@year'),
                    ('station:', '@station'),  # use @{ } for field names with spaces
                    ('count:', '@count'),
                ],
            ))
            # increase the counter to move to next station
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

        source = ColumnDataSource(data={
            'year': years,
            'count': counts,
            'station': list(np.repeat("all stations", len(years)))
        })

        p.line("year", "count", legend=legend_title, line_width=3, line_color='black', line_dash="4 4", source=source)
        p.circle("year", "count", legend=legend_title, fill_color='black', line_color="black", size=8, source=source)

        p.add_tools(HoverTool(
            tooltips=[
                ('year:', '@year'),
                ('station:', '@station'),  # use @{ } for field names with spaces
                ('count:', '@count'),
            ],
        ))

        # p.line(years, counts, legend=legend_title, line_width=3, line_color='black', line_dash="4 4")
        # p.circle(years, counts, legend=legend_title, fill_color='black', line_color='black', size=8)
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

WIDTH = 1200
HEIGHT = 800
TITLE_FONT_SIZE = '16pt'
LEGEND_FONT_SIZE = '12pt'

def generate_annual_watershed_report(site, year):
    # start assigning files and by cleaning the temp dir
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(settings.BASE_DIR, 'static', 'img', 'camp', 'temp')
    target_file_pie = os.path.join(target_dir, 'pie_chart.png')
    target_file_richness = os.path.join(target_dir, 'species_richness.png')
    target_file_do = os.path.join(target_dir, 'do.png')
    target_file_greeb_crab = os.path.join(target_dir, 'green_crab.png')

    try:
        rmtree(target_dir)
    except:
        print("no such dir.")
    os.mkdir(target_dir)

    generate_sub_pie_chart(site, year, target_file_pie)
    generate_sub_species_richness(site, target_file_richness)
    generate_sub_do(site, target_file_do)
    generate_sub_green_crab(site, target_file_greeb_crab)

    return None


def generate_sub_pie_chart(site, year, target_file):
    # species will be represented by percentages of the total number of species observed at a given site
    species_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, ]

    # create a dictionary of species codes by counts
    x = {}
    for s in species_list:
        s_code = models.Species.objects.get(pk=s).code
        s_sum = models.SpeciesObservation.objects.filter(sample__station__site_id=site).filter(
            sample__year=year).filter(
            species_id=s).order_by("species").values('species').distinct().annotate(
            dsum=Sum('total_non_sav'))
        try:
            x[s_code] = s_sum[0]["dsum"]
        except:
            x[s_code] = 0

    # now we need to add the 'other' category
    cum_mod = models.SpeciesObservation.objects.filter(sample__station__site_id=site).filter(sample__year=year)
    for s in species_list:
        s_code = 'Other'
        cum_mod = cum_mod.filter(~Q(species_id=s))

    cum_mod = cum_mod.order_by('sample__station__site_id').values('sample__station__site_id').distinct().annotate(
        dsum=Sum('total_non_sav'))
    try:
        x[s_code] = cum_mod[0]["dsum"]
    except:
        x[s_code] = 0

    # prepare the data for the glyph
    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'species'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['percentage'] = data['value'] / data['value'].sum()
    data['color'] = palettes.Category20[len(x)]
    data['legend_label'] = ["{} - {:.1%}".format(data['species'][i], data['percentage'][i]) for i in range(0, len(x))]

    site_name = str(models.Site.objects.get(pk=site))
    title = "13 Most Common and Rare Species Observed in {} for {}".format(site_name, year)

    # hover = HoverTool(tooltips=[("Species", "@species"),
    #                             ("percentage", "@percentage{%0.2f}")
    #                             ])

    p = figure(plot_height=HEIGHT, plot_width=WIDTH, title=title, toolbar_location=None,
               x_range=(-0.5, 1.0), )
    p.title.text_font_size = TITLE_FONT_SIZE
    p.wedge(x=0, y=0, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend='legend_label', source=data)
    p.legend.label_text_font_size = LEGEND_FONT_SIZE
    total_mod = models.SpeciesObservation.objects.filter(sample__station__site_id=site).filter(
        sample__year=year).order_by('sample__station__site_id').values('sample__station__site_id').distinct().annotate(
        dsum=Sum('total_non_sav'))
    total_abundance = total_mod[0]["dsum"]
    citation = Label(x=0.45, y=-0.7,
                     text='Total abundance = {:,}'.format(total_abundance), render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
    p.add_layout(citation)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    export_png(p, filename=target_file)
    return None


def generate_sub_species_richness(site, target_file):
    # create a new plot
    site_name = str(models.Site.objects.get(pk=site))
    title = "Species Richness by Year at {}".format(site_name)

    p = figure(
        title=title,
        x_axis_label='Year',
        y_axis_label='Species count',
        plot_width=WIDTH, plot_height=HEIGHT,
        x_axis_type="linear",
        toolbar_location=None,

    )
    ticker = SingleIntervalTicker(interval=1)
    p.title.text_font_size = TITLE_FONT_SIZE
    p.grid.grid_line_alpha = 1
    p.background_fill_color = "white"
    p.xaxis.minor_tick_line_color = None
    p.xaxis.ticker = ticker

    # first we need a list of stations
    stations = models.Station.objects.filter(site_id=site).order_by("name")

    # generate color palette
    if len(stations) <= 10:
        colors = palettes.Category10[len(stations)]
    else:
        colors = palettes.Category20[len(stations)]

    i = 0
    for station in stations:
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

        source = ColumnDataSource(data={
            'year': years,
            'count': counts,
            'station': list(np.repeat(str(station), len(years)))
        })

        p.line("year", "count", legend=legend_title, line_width=1, line_color=colors[i], source=source)
        p.circle("year", "count", legend=legend_title, fill_color=colors[i], line_color=colors[i], size=3,
                 source=source)
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

    source = ColumnDataSource(data={
        'year': years,
        'count': counts,
        'station': list(np.repeat("all stations", len(years)))
    })

    p.line("year", "count", legend=legend_title, line_width=3, line_color='black', line_dash="4 4", source=source)
    p.circle("year", "count", legend=legend_title, fill_color='black', line_color="black", size=8, source=source)
    p.legend.label_text_font_size = LEGEND_FONT_SIZE
    export_png(p, filename=target_file)


def generate_sub_do(site, target_file):
    # create a new plot
    site_name = str(models.Site.objects.get(pk=site))
    title = "Dissolved Oxygen by Year at {}".format(site_name)

    p = figure(
        title=title,
        x_axis_label='Year',
        y_axis_label='Dissolved oxygen (mg/l)',
        plot_width=WIDTH, plot_height=HEIGHT,
        x_axis_type="linear",
        toolbar_location=None,
    )
    ticker = SingleIntervalTicker(interval=1)
    p.title.text_font_size = TITLE_FONT_SIZE

    p.grid.grid_line_alpha = 1
    p.background_fill_color = "white"
    p.xaxis.minor_tick_line_color = None
    p.xaxis.ticker = ticker

    # first we need a list of stations
    stations = models.Station.objects.filter(site_id=site).order_by("name")

    # generate color palette
    if len(stations) <= 10:
        colors = palettes.Category10[len(stations)]
    else:
        colors = palettes.Category20[len(stations)]

    i = 0
    for station in stations:
        qs_years = models.Sample.objects.filter(station=station).order_by("year").values(
            'year',
        ).distinct()

        years = []
        do_max = []
        do_min = []
        do_avg = []

        for obj in qs_years:
            y = obj['year']
            do_readings = [obj.dissolved_o2 for obj in models.Sample.objects.filter(year=y).filter(station=station)]
            do_readings = list(filter(None, do_readings))
            do_max.append(max(do_readings))
            do_min.append(min(do_readings))
            do_avg.append(statistics.mean(do_readings))
            years.append(y)
        legend_title = str(station)

        source = ColumnDataSource(data={
            'stations': list(np.repeat(str(station), len(years))),
            'years': years,
            'do_max': do_max,
            'do_min': do_min,
            'do_avg': do_avg,
        })

        p.segment("years", "do_max", "years", "do_min", color=colors[i], source=source)
        p.line("years", "do_avg", legend=legend_title, line_width=1, line_color=colors[i], source=source)
        p.circle("years", "do_avg", legend=legend_title, fill_color=colors[i], line_color=colors[i], size=3,
                 source=source)
        i += 1

    # show(p)
    p.legend.label_text_font_size = LEGEND_FONT_SIZE
    export_png(p, filename=target_file)


def generate_sub_green_crab(site, target_file):
    # create a new plot
    site_name = str(models.Site.objects.get(pk=site))
    title = "Annual Number of Green Crabs Caught in the {} Watershed".format(site_name)

    color = palettes.BuGn[5][2]

    years = [obj["year"] for obj in models.Sample.objects.order_by("year").values('year').distinct()]
    counts = []
    for year in years:
        green_crab_sum = models.SpeciesObservation.objects.filter(sample__station__site_id=site).filter(
            sample__year=year).filter(species_id=18).order_by("species").values('species').distinct().annotate(
            dsum=Sum('total_non_sav'))
        try:
            counts.append(green_crab_sum[0]["dsum"])
        except:
            counts.append(0)

    years = [str(y) for y in years]
    source = ColumnDataSource(data={
        'years': years,
        'counts': counts,
    })
    p = figure(x_range=years, toolbar_location=None, plot_width=WIDTH, plot_height=HEIGHT, title=title)
    p.vbar(x='years', top='counts', width=0.9, source=source, line_color='white', fill_color=color)
    p.title.text_font_size = TITLE_FONT_SIZE

    labels = LabelSet(x='years', y='counts', text='counts', level='glyph',
                      x_offset=-10, y_offset=5, source=source, render_mode='canvas')
    p.add_layout(labels)

    # show(p)
    export_png(p, filename=target_file)
