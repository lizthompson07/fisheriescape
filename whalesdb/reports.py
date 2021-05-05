import csv
from . import models
from django.http import HttpResponse


def report_deployment_summary(query_params):
    qs = models.EdaEquipmentAttachment.objects.all()

    filter_list = [
        "year",
        "month",
        "station",
    ]
    for filter in filter_list:
        input = query_params.get(filter)
        if input == "true":
            input = True
        elif input == "false":
            input = False
        elif input == "null" or input == "":
            input = None

        if input:
            if filter == "year":
                qs = qs.filter(dep__dep_year=input)
            elif filter == "month":
                qs = qs.filter(dep__dep_month=input)
            elif filter == "station":
                qs = qs.filter(dep__stn=input)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="deployment_summary.csv"'

    writer = csv.writer(response)
    writer.writerow(['EDA_ID', 'Year', 'Month', 'Deployment', 'Station', 'Latitude', 'Longitude', 'Depth_m', 'Equipment make_model_serial',
                     'Hydrophone make_model_serial', 'Dataset timezone', 'Recording schedule', 'In-water_start',
                     'In-water_end', 'Dataset notes'])

    qs = qs.order_by("dep__stn__stn_name").order_by("dep__dep_month").order_by("-dep__dep_year")
    for q in qs:
        deployment = q.dep
        eqp = q.eqp

        year = deployment.dep_year
        month = deployment.dep_month

        datasets = q.dataset.all()

        for dataset in datasets:
            staion_events = deployment.station_events.filter(set_type=1)  # set_type=1 is the deployment event
            for dep_evt in staion_events:
                lat = dep_evt.ste_lat_mcal if dep_evt.ste_lat_mcal else dep_evt.ste_lat_ship
                lon = dep_evt.ste_lon_mcal if dep_evt.ste_lon_mcal else dep_evt.ste_lon_ship
                depth = dep_evt.ste_depth_mcal if dep_evt.ste_depth_mcal else dep_evt.ste_lon_ship

                in_start_date = dataset.rec_start_date
                in_start_time = dataset.rec_start_time
                in_start = "{} {}".format(in_start_date, in_start_time)

                in_end_date = dataset.rec_end_date
                in_end_time = dataset.rec_end_time
                in_end = "{} {}".format(in_end_date, in_end_time)

                hydro = q.eqp.hydrophones.filter(ehe_date__lte=in_start_date).order_by("ehe_date").last()
                hyd = hydro.hyd if hydro else "----"
                writer.writerow([q.pk, year, month, dep_evt.dep.dep_name, dep_evt.dep.stn, lat, lon, depth, eqp,
                                hyd, dataset.rtt_dataset, dataset.rsc_id, in_start,
                                in_end, dataset.rec_notes])

    return response
