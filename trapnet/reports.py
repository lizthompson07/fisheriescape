import unicodecsv as csv
from django.db.models import Sum, Avg
from django.http import HttpResponse
from django.template.defaultfilters import floatformat

from lib.functions.custom_functions import listrify
from . import models


def generate_sample_report(year, sites):
    if year != "None":
        qs = models.Sample.objects.filter(season=year).filter(site__exclude_data_from_site=False)
        filename = "sample_report_{}.csv".format(year)
    else:
        qs = models.Sample.objects.all().filter(site__exclude_data_from_site=False)
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
        qs = models.Entry.objects.filter(sample__season=year).filter(sample__site__exclude_data_from_site=False)
        filename = "entry_report_{}.csv".format(year)
    else:
        qs = models.Entry.objects.all().filter(sample__site__exclude_data_from_site=False)
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


def generate_open_data_ver_1_data_dictionary():
    """
    Generates the data dictionary for open data report version 1
    """

    filename = "open_data_ver1_data_dictionary.csv"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    writer.writerow("")
    writer.writerow(["Abiotic variables / Variables abiotiques:".upper(), ])
    writer.writerow(["#########################################", ])
    # write the header
    header = [
        "name__nom",
        "description_en",
        "description_fr",
    ]
    writer.writerow(header)

    field_names = [
        'year',
        'site_name',
        'site_latitude',
        'site_longitude',
        'avg_air_temp_arrival',
        'avg_max_air_temp',
        'avg_water_temp_shore',
    ]

    descr_eng = [
        "sample year",
        "name of site and river",
        "site latitude (decimal degrees)",
        "site longitude (decimal degrees)",
        "average air temperature on arrival (degrees C)",
        "average max air temperature (degrees C)",
        "average water temperature taken from shore (degrees C)",
    ]
    descr_fra = [
        "année-échantillon",
        "nom du site et de la rivière",
        "latitude du site (degrés décimaux)",
        "longitude du site (degrés décimaux)",
        "température moyenne de l'air à l'arrivée (degrés C)",
        "température maximale moyenne de l'air (degrés C)",
        "température moyenne de l'eau prise du rivage (degrés C)",
    ]

    for i in range(0, len(field_names)):
        writer.writerow([
            field_names[i],
            descr_eng[i],
            descr_fra[i],
        ])

    writer.writerow("")
    writer.writerow("")
    writer.writerow("")
    writer.writerow(["Biotic variables / Variables biotiques:".upper(), ])
    writer.writerow(["#######################################", ])
    field_names = [
        "X_abundance",
        "X_avg_fork_length",
        "X_avg_total_length",
        "X_avg_weight",
    ]

    descr_eng = [
        "total abundance of species X for a given site and year",
        "mean fork length (mm) of species X for a given site and year",
        "mean total length (mm) of species X for a given site and year; this is only provided for American eel",
        "mean weight (g) of species X for a given site and year",
    ]
    descr_fra = [
        "Abondance totale de l'espèce X pour un site et une année donnés",
        "longueur à la fourche moyenne (mm) de l'espèce X pour un site et une année donnés",
        "longueur totale moyenne (mm) de l'espèce X pour un site et une année donnés; prévu que pour l'anguille d'Amérique",
        "poids moyen (g) de l'espèce X pour un site et une année donnés",
    ]
    for i in range(0, len(field_names)):
        writer.writerow([
            field_names[i],
            descr_eng[i],
            descr_fra[i],
        ])

    writer.writerow("")
    writer.writerow("")
    writer.writerow("")
    writer.writerow(["Species / Espèces:".upper()])
    writer.writerow(["##################"])
    # write the header
    header = [
        "code",
        "common_name_en__nom_commun_en",
        "common_name_en__nom_commun_fr",
        "life_stage_en__étape_de_vie_en",
        "life_stage_fr__étape_de_vie_fr",
        "scientific_name__nom_scientifique",
        "ITIS_TSN",
    ]
    writer.writerow(header)

    for sp in models.Species.objects.all():
        life_stage_eng = sp.life_stage.name if sp.life_stage else None
        life_stage_fra = sp.life_stage.nom if sp.life_stage else None

        writer.writerow([
            sp.abbrev,
            sp.common_name_eng,
            sp.common_name_fre,
            life_stage_eng,
            life_stage_fra,
            sp.scientific_name,
            sp.tsn,
        ])

    return response


def generate_open_data_ver_1_report(year, sites):
    """
    This is a view designed for FGP / open maps view. The resulting csv will summarize data per site per year

    :param year: int
    :param sites: list of river site PKs
    :return: http response
    """

    # It is important that we remove any samples taken at MAtapedia River since these data do not belong to us.
    if year != "None":
        qs = models.Entry.objects.filter(sample__season=year).filter(sample__site__exclude_data_from_site=False)
        filename = "open_data_ver1_report_{}.csv".format(year)
    else:
        qs = models.Entry.objects.all().filter(sample__site__exclude_data_from_site=False)
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
        'avg_air_temp_arrival',
        'avg_max_air_temp',
        'avg_water_temp_shore',
    ]

    for species in species_list:
        if species.id == 54:
            addendum = [
                "{}_abundance".format(species.abbrev),
                "{}_avg_total_length".format(species.abbrev),
                "{}_avg_weight".format(species.abbrev),
            ]
        else:
            addendum = [
                "{}_abundance".format(species.abbrev),
                "{}_avg_fork_length".format(species.abbrev),
                "{}_avg_weight".format(species.abbrev),
            ]
        header_row.extend(addendum)

    writer.writerow(header_row)

    # lets start by getting a list of samples and years
    # samples = [models.Sample.objects.get(pk=obj["sample"]) for obj in qs.order_by("sample").values("sample").distinct()]
    sites = [models.RiverSite.objects.get(pk=obj["sample__site"]) for obj in qs.order_by("sample__site").values("sample__site").distinct()]
    years = [obj["sample__season"] for obj in qs.order_by("sample__season").values("sample__season").distinct()]

    for year in years:
        for site in sites:
            data_row = [
                year,
                site,
                site.latitude_n,
                site.longitude_w,
                floatformat(qs.filter(sample__season=year, sample__site=site, ).values("sample").order_by("sample").distinct().aggregate(
                    davg=Avg("sample__air_temp_arrival"))["davg"], 3),
                floatformat(qs.filter(sample__season=year, sample__site=site, ).values("sample").order_by("sample").distinct().aggregate(
                    davg=Avg("sample__max_air_temp"))["davg"], 3),
                floatformat(qs.filter(sample__season=year, sample__site=site, ).values("sample").order_by("sample").distinct().aggregate(
                    davg=Avg("sample__water_temp_shore_c"))["davg"], 3),
            ]

            for species in species_list:
                if species.id == 54:
                    addendum = [
                        qs.filter(sample__season=year, sample__site=site, species=species).values("frequency").order_by(
                            "frequency").aggregate(
                            dsum=Sum("frequency"))["dsum"],
                        floatformat(qs.filter(sample__season=year, sample__site=site, species=species).values("fork_length").order_by(
                            "fork_length").aggregate(davg=Avg("total_length"))["davg"], 3),
                        floatformat(qs.filter(sample__season=year, sample__site=site, species=species).values("weight").order_by(
                            "weight").aggregate(davg=Avg("weight"))["davg"], 3),
                    ]
                else:
                    addendum = [
                        qs.filter(sample__season=year, sample__site=site, species=species).values("frequency").order_by(
                            "frequency").aggregate(
                            dsum=Sum("frequency"))["dsum"],
                        floatformat(qs.filter(sample__season=year, sample__site=site, species=species).values("fork_length").order_by(
                            "fork_length").aggregate(davg=Avg("fork_length"))["davg"], 3),
                        floatformat(qs.filter(sample__season=year, sample__site=site, species=species).values("weight").order_by(
                            "weight").aggregate(davg=Avg("weight"))["davg"], 3),
                    ]
                data_row.extend(addendum)

            writer.writerow(data_row)

    return response


def generate_open_data_ver_1_wms_report():
    """
    Simple report for web mapping service on FGP
    """
    # It is important that we remove any samples taken at MAtapedia River since these data do not belong to us.
    qs = models.Entry.objects.all().filter(sample__site__exclude_data_from_site=False)
    filename = "open_data_ver1_wms_report.csv"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    # headers are based on csv provided by GD
    species_list = [models.Species.objects.get(pk=obj["species"]) for obj in qs.order_by("species").values("species").distinct()]

    header_row_eng = [
        'Site name',
        'Site latitude',
        'Site longitude',
        'Seasons in operation',
        'List of species caught (English)',
        'List of species caught (French)',
        'Total number of fish caught',
        'Average (mean) number of fish caught',
    ]

    header_row_fre = [
        'Nom de site',
        'Latitude de site',
        'Longitude de site',
        'Saisons en opération',
        'Liste des espèces capturées (anglais)',
        'Liste des espèces capturées (français)',
        'Nombre total de poisson capturées',
        'Nombre moyen (moyen) de poissons capturés',
    ]

    writer.writerow(header_row_eng)
    writer.writerow(header_row_fre)

    # lets start by getting a list of samples and years
    # samples = [models.Sample.objects.get(pk=obj["sample"]) for obj in qs.order_by("sample").values("sample").distinct()]
    sites = [models.RiverSite.objects.get(pk=obj["sample__site"]) for obj in qs.order_by("sample__site").values("sample__site").distinct()]

    for site in sites:
        seasons = listrify(
            [obj["sample__season"] for obj in qs.filter(sample__site=site).order_by("sample__season").values("sample__season").distinct()])
        spp_list_eng = listrify([models.Species.objects.get(pk=obj["species"]).common_name_eng for obj in
                                 qs.filter(sample__site=site).order_by("species").values("species").distinct()])
        spp_list_fra = listrify([models.Species.objects.get(pk=obj["species"]).common_name_fre for obj in
                                 qs.filter(sample__site=site).order_by("species").values("species").distinct()])
        total_freq = qs.filter(sample__site=site, ).values("frequency").order_by("frequency").aggregate(
            dsum=Sum("frequency"))["dsum"]
        avg_freq = floatformat(int(total_freq) / len(seasons.split(",")), 2)

        data_row = [
            site,
            site.latitude_n,
            site.longitude_w,
            seasons,
            spp_list_eng,
            spp_list_fra,
            total_freq,
            avg_freq,
        ]

        writer.writerow(data_row)

    return response
