from bokeh.plotting import figure, output_file, save


def generate_species_count_report(counts, years, sp, filename):
    # prepare  data
    x = years
    y0 = counts
    # y1 = [10 ** i for i in x]
    # y2 = [10 ** (i ** 2) for i in x]

    # output to static HTML file
    output_file(filename)

    # create a new plot
    p = figure(
        tools="pan,box_zoom,wheel_zoom,reset,save",
        x_axis_label='Year',
        y_axis_label='Count'
    )

    # add some renderers
    legend_title = "Total annual observations for {}".format(sp)
    p.line(x, y0, legend=legend_title)
    p.circle(x, y0, legend=legend_title, fill_color="white", size=8)
    # p.line(x, y0, legend="y=x^2", line_width=3)
    # p.line(x, y1, legend="y=10^x", line_color="red")
    # p.circle(x, y1, legend="y=10^x", fill_color="red", line_color="red", size=6)
    # p.line(x, y2, legend="y=10^x^2", line_color="orange", line_dash="4 4")

    # show the results
    # show(p)
    save(p)
