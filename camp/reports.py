from bokeh.plotting import figure, output_file, save
from django.db.models import Sum, Count
from shutil import rmtree
from . import models

import numpy as np
import os

N = 100
x = np.random.random(size=N) * 100
y = np.random.random(size=N) * 100
colors = [
    "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*x, 30+2*y)
]
#
# colors = [
#     'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black', 'blanchedalmond',
#     'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue',
#     'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey',
#     'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon',
#     'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink',
#     'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia',
#     'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey', 'honeydew', 'hotpink',
#     'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue',
#     'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink',
#     'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue',
#     'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue',
#     'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise',
#     'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace',
#     'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise',
#     'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'red', 'rosybrown',
#     'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue',
#     'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato',
#     'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen'
# ]


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

    i = 0
    for obj in my_list:
        sp_id = int(obj.replace("'", ""))
        # create a new file containing data
        qs = models.SpeciesObservation.objects.filter(species=sp_id).values(
            'sample__year'
        ).distinct().annotate(dsum=Sum('total'))

        years = [i["sample__year"] for i in qs]
        counts = [i["dsum"] for i in qs]
        my_sp = models.Species.objects.get(pk=sp_id)
        legend_title = "Annual observations for {}".format(my_sp.common_name_eng)
        p.line(years, counts, legend=legend_title, line_color=colors[i], line_width=3)
        p.circle(years, counts, legend=legend_title, fill_color=colors[i], line_color=colors[i], size=8)
        i += 1

    save(p)


def generate_species_richness_report():
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
        x_axis_type="linear"

    )

    p.grid.grid_line_alpha = 1
    qs_years = models.Sample.objects.all().order_by("year").values(
        'year',
    ).distinct()

    years = []
    counts = []

    for obj in qs_years:
        y = obj['year']
        annual_obs = models.SpeciesObservation.objects.filter(sample__year=y).values(
            'species_id',
        ).distinct()
        species_set = set([i["species_id"] for i in annual_obs])
        years.append(y)
        print(years)
        counts.append(len(species_set))
        print(counts)
    # my_sp = models.Species.objects.get(pk=sp_id)
    legend_title = "Number of species observed"
    p.line(years, counts, legend=legend_title, line_width=3)
    p.circle(years, counts, legend=legend_title, fill_color='white', size=8)
    # TODO: should we show the number of stations visited?
    save(p)

# TODO: number of species observed by year at a giving station..
# it can be combined with this one but instead of selecting a station there would be an all option
