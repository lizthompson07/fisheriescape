import unicodecsv as csv
from django.db.models import Sum
from django.http import HttpResponse
from . import models


def generate_sample_report(year, sites):
    if year != "None":
        qs = models.Sample.objects.filter(season=year)
        filename = "sample_report_{}.csv".format(year)
    else:
        qs = models.Sample.objects.all()
        filename = "sample_report_all_years.csv"

    if sites != "None":
        qs = qs.filter(site_id__in=sites.split(","))

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    # headers are based on csv provided by GD
    writer.writerow([
        # 'River',
        # 'Year',
        # 'Month',
        # 'Day',
        # 'Time_arrival',
        # 'Time_departure',
        # 'Airtemp_arrival',
        # 'Airtemp_min',
        # 'Airtemp_max',
        # 'Cloud_cover_pcent',
        # 'Precipitation',
        # 'Wind',
        # 'Water_level',
        # 'Discharge_m3_sec',
        # 'Water_temperature_shore',
        # 'VEMCO',
        # 'RPM_arrival',
        # 'RPM_departure',
        # 'Operating_condition',
        # 'Crew',
        # 'Comments',
        'id',
        'site',
        'sample_type',
        'arrival_date',
        'departure_date',
        'year',
        'month',
        'day',
        'arrival_time',
        'departure_time',
        'air_temp_arrival',
        'min_air_temp',
        'max_air_temp',
        'percent_cloud_cover',
        'precipitation_category',
        'precipitation_comment',
        'wind_speed',
        'wind_direction',
        'water_depth_m',
        'water_level_delta_m',
        'discharge_m3_sec',
        'water_temp_shore_c',
        'water_temp_trap_c',
        'rpm_arrival',
        'rpm_departure',
        'operating_condition',
        'operating_condition_comment',
        'samplers',
        'notes',
        'season',
        'last_modified',
        'last_modified_by',
    ])

    for sample in qs:
        writer.writerow(
            [
                sample.id,
                sample.site,
                sample.sample_type,
                sample.arrival_date,
                sample.departure_date,
                sample.arrival_date.year,
                sample.arrival_date.month,
                sample.arrival_date.day,
                sample.arrival_date.strftime("%H:%M"),
                sample.departure_date.strftime("%H:%M"),
                sample.air_temp_arrival,
                sample.min_air_temp,
                sample.max_air_temp,
                sample.percent_cloud_cover,
                sample.precipitation_category,
                sample.precipitation_comment,
                sample.wind_speed,
                sample.wind_direction,
                sample.water_depth_m,
                sample.water_level_delta_m,
                sample.discharge_m3_sec,
                sample.water_temp_shore_c,
                sample.water_temp_trap_c,
                sample.rpm_arrival,
                sample.rpm_departure,
                sample.operating_condition,
                sample.operating_condition_comment,
                sample.samplers,
                sample.notes,
                sample.season,
                sample.last_modified,
                sample.last_modified_by,
            ])

    return response


def generate_entry_report(year, sites):
    if year != "None":
        qs = models.Entry.objects.filter(sample__season=year)
        filename = "entry_report_{}.csv".format(year)
    else:
        qs = models.Entry.objects.all()
        filename = "entry_report_all_years.csv"

    if sites != "None":
        qs = qs.filter(sample__site_id__in=sites.split(","))

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    # headers are based on csv provided by GD
    writer.writerow([
        'sample_id',
        'site_name',
        'species_name',
        'species_code',
        'first_tag',
        'last_tag',
        'status_name',
        'status_code',
        'origin_code',
        'frequency',
        'fork_length',
        'total_length',
        'weight',
        'sex',
        'smolt_age',
        'location_tagged',
        'date_tagged',
        'scale_id_number',
        'tags_removed',
        'notes',
    ])

    for entry in qs:
        origin = entry.origin.code if entry.origin else None

        writer.writerow(
            [
                entry.sample_id,
                entry.sample.site,
                entry.species,
                entry.species.code,
                entry.first_tag,
                entry.last_tag,
                entry.status.name,
                entry.status.code,
                origin,
                entry.frequency,
                entry.fork_length,
                entry.total_length,
                entry.weight,
                entry.sex,
                entry.smolt_age,
                entry.location_tagged,
                entry.date_tagged,
                entry.scale_id_number,
                entry.tags_removed,
                entry.notes,
            ])

    return response


def generate_open_data_ver_1_report(year, sites):
    """
    This is a view designed for FGP / open maps view. The resulting csv will summarize data per site per year

    :param year:
    :param sites:
    :return:
    """

    if year != "None":
        qs = models.Entry.objects.filter(sample__season=year)
        filename = "open_data_ver1_report_{}.csv".format(year)
    else:
        qs = models.Entry.objects.all()
        filename = "open_data_ver1_report_all_years.csv"

    if sites != "None":
        qs = qs.filter(sample__site_id__in=sites.split(","))

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    # headers are based on csv provided by GD
    species_list = [models.Species.objects.get(pk=obj["species"]) for obj in qs.order_by("species").values("species").distinct()]

    header_row = [
        'year',
        'site_name',
        'site_latitude',
        'site_longitude',
        'avg_air_temp_on_arrival',
        'avg_max_air_temp',
        'avg_water_temp',
    ]

    for species in species_list:
        addendum = [
            "{}_abundance".format(species.abbrev),
            "{}_avg_fork_length".format(species.abbrev),
            "{}_avg_weight".format(species.abbrev),
        ]
        header_row.extend(addendum)

    writer.writerow(header_row)

    # lets start by getting a list of samples and years
    samples = [models.Sample.objects.get(pk=obj["sample"]) for obj in qs.order_by("sample").values("sample").distinct()]
    sites = [models.RiverSite.objects.get(pk=obj["sample__site"]) for obj in qs.order_by("sample__site").values("sample__site").distinct()]
    years = [obj["sample__season"] for obj in qs.order_by("sample__season").values("sample__season").distinct()]

    for year in years:
        for site in sites:
            data_row = [
                year,
                site,
            ]
            for species in species_list:
                # addendum = [
                #     qs.order_by("sample__site").values("sample__site")
                #
                #     qs.filter(sample__season=year, sample__site=site, species=species).values("frequency").order_by("frequency").annotate(dsum=Sum("invoice_cost")).first()["dsum"]
                #     ,
                #     "{}_avg_fork_length".format(species.abbrev),
                #     "{}_avg_weight".format(species.abbrev),
                # ]
                data_row.extend(addendum)

            writer.writerow(data_row)


    project_adjustments = models.Entry.objects.filter(season=year, ).filter(exclude_from_rollup=False).filter(fiscal_year=fy).filter(
                                transaction_type=2).filter(allotment_code=ac).values(
                                "project").order_by("project").distinct().annotate(dsum=Sum("invoice_cost")).first()["dsum"]

    return response
