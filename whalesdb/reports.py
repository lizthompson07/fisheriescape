import csv
from . import models
from django.http import HttpResponse


def report_deployment_summary(query_params):
    qs = models.EdaEquipmentAttachment.objects.all()

    filter_list = [
        "start_date",
        "end_date",
        "station",
        "project",
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
            if filter == "start_date":
                date = input.split("-")
                qs = qs.exclude(dep__dep_year__lt=date[0])
                qs = qs.exclude(dep__dep_year=date[0], dep__dep_month__lt=date[1])
            elif filter == "end_date":
                date = input.split("-")
                qs = qs.exclude(dep__dep_year__gt=date[0])
                qs = qs.exclude(dep__dep_year=date[0], dep__dep_month__gt=date[1])
            elif filter == "station":
                lst = query_params.getlist('station')
                qs = qs.filter(dep__stn__in=lst)
            elif filter == "project":
                lst = query_params.getlist('project')
                qs = qs.filter(dep__prj__in=lst)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="deployment_summary.csv"'

    writer = csv.writer(response)
    writer.writerow(['EDA_ID', 'Year', 'Month', 'Deployment', 'Station', "Project", 'Latitude', 'Longitude', 'Depth_m',
                     'Equipment make_model_serial', 'Hydrophone make_model_serial', 'Dataset timezone',
                     'Recording schedule', 'In-water_start', 'In-water_end', 'Dataset notes'])

    qs = qs.order_by("dep__stn__stn_name").order_by("-dep__dep_month").order_by("-dep__dep_year")
    for q in qs:
        deployment = q.dep
        eqp = q.eqp

        year = deployment.dep_year
        month = deployment.dep_month

        staion_events = deployment.station_events.filter(set_type=1)  # set_type=1 is the deployment event
        for dep_evt in staion_events:
            lat = dep_evt.ste_lat_mcal if dep_evt.ste_lat_mcal else dep_evt.ste_lat_ship
            lon = dep_evt.ste_lon_mcal if dep_evt.ste_lon_mcal else dep_evt.ste_lon_ship
            depth = dep_evt.ste_depth_mcal if dep_evt.ste_depth_mcal else dep_evt.ste_depth_ship

            hydro = q.eqp.hydrophones.all()

            hydro = hydro.filter(ehe_date__lte=dep_evt.ste_date)

            hydro = hydro.order_by("ehe_date").last()

            hyd = "----"
            if hydro:
                hyd = hydro.hyd

            datasets = q.dataset.all()
            if len(datasets) > 0:
                for dataset in datasets:
                    in_start = "NA"
                    in_end = "NA"

                    in_start_date = dataset.rec_start_date
                    in_start_time = dataset.rec_start_time
                    if in_start_date or in_start_time:
                        in_start = "{} {}".format(in_start_date, in_start_time)

                    in_end_date = dataset.rec_end_date
                    in_end_time = dataset.rec_end_time
                    if in_end_date or in_end_time:
                        in_end = "{} {}".format(in_end_date, in_end_time)

                    writer.writerow([q.pk, year, month, dep_evt.dep.dep_name, dep_evt.dep.stn, dep_evt.dep.prj, lat,
                                     lon, depth, eqp, hyd, dataset.rtt_dataset, dataset.rsc_id, in_start, in_end,
                                     dataset.rec_notes])
            else:
                writer.writerow([q.pk, year, month, dep_evt.dep.dep_name, dep_evt.dep.stn, dep_evt.dep.prj, lat, lon,
                                 depth, eqp, hyd, "NA", "NA", "NA", "NA", "NA"])

    return response
