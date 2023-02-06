from copy import deepcopy

import unicodecsv as csv
from django.db.models import Sum, Avg, Q
from django.http import HttpResponse
from django.template.defaultfilters import floatformat, slugify

from dm_apps.utils import Echo, get_timezone_time
from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from . import models


def generate_sample_csv(qs):
    """Returns a generator for an HTTP Streaming Response"""

    fields = models.Sample._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)

    field_names.remove("site")
    field_names.remove("id")
    try:
        field_names.remove("air_temp_arrival")
        field_names.remove("water_temp_c")
    except:
        pass

    header_row = deepcopy(field_names)
    header_row += [
        "sample_id",
        "sample_type_display",
        "precipitation_category_display",
        "wind_speed_display",
        "wind_direction_display",
        "didymo_display",
        "river_name",
        "site_name",
        "fishing_area",
        "river_cgndb",
    ]
    # now we need to determine what fields to append from the sample subtype
    is_ef = False
    is_rst = False
    is_trapnet = False
    sub_field_names = list()
    if qs.exists():
        sub_obj = qs.first().get_sub_obj()
        sub_field_names = [field.name for field in sub_obj._meta.fields]
        sub_field_names.remove("sample")
        sub_field_names.remove("id")
        header_row += sub_field_names
        if isinstance(sub_obj, models.EFSample):
            is_ef = True
            header_row += [
                "site_type_display",
                "seine_type_display",
                "electrofisher_pulse_type_display",
                "avg_wetted_length",
                "avg_wetted_width",
                "full_wetted_area",
            ]
        elif isinstance(sub_obj, models.RSTSample):
            is_rst = True
            header_row += [
                "operating_condition_display",
            ]
        elif isinstance(sub_obj, models.TrapnetSample):
            is_trapnet = True
            header_row += [
                "sea_lice_display",
            ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    sorted_header = sorted(header_row)
    yield writer.writerow(sorted_header)
    print(sorted_header)

    for obj in qs:
        sub_obj = obj.get_sub_obj()
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]
        data_row += [
            obj.id,
            obj.get_sample_type_display(),
            obj.get_precipitation_category_display(),
            obj.get_wind_speed_display(),
            obj.get_wind_direction_display(),
            obj.get_didymo_display(),
            obj.site.river.name,
            obj.site.name,
            obj.site.river.fishing_area,
            obj.site.river.cgndb,
        ]
        data_row += [str(nz(getattr(sub_obj, field), "")).encode("utf-8").decode('utf-8') for field in sub_field_names]
        if is_ef:
            data_row += [
                sub_obj.get_site_type_display(),
                sub_obj.get_seine_type_display(),
                sub_obj.get_electrofisher_pulse_type_display(),
                sub_obj.avg_wetted_length,
                sub_obj.avg_wetted_width,
                sub_obj.full_wetted_area,
            ]
        elif is_rst:
            data_row += [
                sub_obj.get_operating_condition_display(),
            ]
        elif is_trapnet:
            data_row += [
                sub_obj.get_sea_lice_display(),
            ]

        sorted_data_row = [x for _, x in sorted(zip(header_row, data_row))]
        yield writer.writerow(sorted_data_row)


def generate_sweep_csv(qs):
    """Returns a generator for an HTTP Streaming Response"""

    header_row = [
        "SFA",
        "monitoring_program",
        "cgndb",
        "river_name",
        "site_name",
        "date",
        "day of the year[1 - 365]",
        "avg_wetted_length",
        "avg_wetted_width",
        "full_wetted_area",
        "electrofisher",
        "sweep_number",
        "sweep_time",
        "salmon_0plus",
        "salmon_1plus",
        "salmon_2plus",
        "salmon_3plus",
        "salmon_age_unknown",
        "other_species",
        "sample",
        "sample_id",
        "site_event_code",
        "sweep_id",
    ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    for obj in qs:
        age_breakdown = obj.get_salmon_age_breakdown()
        data_row = [
            obj.sample.site.river.fishing_area,  # SFA
            obj.sample.monitoring_program,  # monitoring_program
            obj.sample.site.river.cgndb,  # cgndb
            obj.sample.site.river.name,  # river_name
            obj.sample.site.name,  # site_name
            obj.sample.arrival_date.strftime("%Y-%m-%d"),  # date
            int(obj.sample.arrival_date.strftime("%j")),  # day of the year[1 - 365]
            obj.sample.ef_sample.avg_wetted_length,  # avg_wetted_length
            obj.sample.ef_sample.avg_wetted_width,  # avg_wetted_width
            obj.sample.ef_sample.full_wetted_area,  # full_wetted_area
            obj.sample.ef_sample.electrofisher.name if obj.sample.ef_sample.electrofisher else "",  # electrofisher
            obj.sweep_number,  # sweep_number
            obj.sweep_time,  # sweep_time
            age_breakdown.get(0, 0),  # salmon_0plus
            age_breakdown.get(1, 0),  # salmon_1plus
            age_breakdown.get(2, 0),  # salmon_2plus
            age_breakdown.get(3, 0),  # salmon_3plus
            age_breakdown.get(None, 0),  # salmon_age_unknown
            obj.specimens.filter(~Q(species__tsn=161996)).order_by("species").values("species").distinct().count(),  # other_species
            f"{obj.sample.get_sample_type_display()} ({obj.sample.id})",  # sample
            obj.sample.id,  # sample_id
            obj.site_event_code,  # site_event_code
            obj.id,  # sweep_id
        ]
        yield writer.writerow(data_row)


def generate_specimen_csv(qs, sample_type):
    """Returns a generator for an HTTP Streaming Response"""

    fields = models.Specimen._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names and field.attname:
            field_names.append(field.attname)

    field_names.remove("id")
    field_names.remove("sweep")
    field_names.remove("sweep_id")
    field_names.remove("origin")
    field_names.remove("origin_id")
    field_names.remove("age_type")
    field_names.remove("river_age")

    header_row = deepcopy(field_names)
    header_row += [
        "specimen_id",
        "site_id",
        "site_name",
        "river_name",
        "arrival_date",
        "departure_date",
        "adipose_condition_display",
        "smart_river_age_type_display",
        "calc_river_age",
    ]

    # now we need to determine what fields to append from the sample subtype
    is_ef = False
    is_rst = False
    is_trapnet = False

    if sample_type == 2:
        is_ef = True
        header_row += [
            "sweep_id",
            "sweep_number",
            "sweep_time",
            "full_wetted_area",
        ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    sorted_header = sorted(header_row)
    yield writer.writerow(sorted_header)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]
        data_row += [
            obj.id,
            obj.sample.site_id,
            obj.sample.site.name,
            obj.sample.site.river.name,
            obj.sample.arrival_date,
            obj.sample.departure_date,
            obj.get_adipose_condition_display(),
            obj.get_smart_river_age_type_display(),
            obj.get_calc_river_age(),
        ]

        if is_ef:
            sub_obj = obj.sample.get_sub_obj()
            data_row += [
                obj.sweep_id,
                obj.sweep.sweep_number,
                obj.sweep.sweep_time,
                sub_obj.full_wetted_area,
            ]
        sorted_data_row = [x for _, x in sorted(zip(header_row, data_row))]
        yield writer.writerow(sorted_data_row)


def generate_river_sites_csv(qs):
    """Returns a generator for an HTTP Streaming Response"""

    fields = models.RiverSite._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names and field.attname:
            field_names.append(field.attname)

    field_names.remove("river")
    field_names.remove("name")
    field_names.remove("id")

    header_row = deepcopy(field_names)
    header_row += [
        "site_id",
        "site_name",
        "river_name",
        "fishing_area",
        "maritime_river_code",
        "old_maritime_river_code",
        "cgndb",
        "parent_cgndb_id",
        "nbadw_water_body_id",
        "parent_river",
        "display_hierarchy",
    ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    sorted_header = sorted(header_row)
    yield writer.writerow(sorted_header)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]
        data_row += [
            obj.id,
            obj.name,
            obj.river.name,
            obj.river.fishing_area,
            obj.river.maritime_river_code,
            obj.river.old_maritime_river_code,
            obj.river.cgndb,
            obj.river.parent_cgndb_id,
            obj.river.nbadw_water_body_id,
            obj.river.parent_river,
            obj.river.display_hierarchy,
        ]
        sorted_data_row = [x for _, x in sorted(zip(header_row, data_row))]
        yield writer.writerow(sorted_data_row)


def generate_biological_detailing_csv(qs):
    """Returns a generator for an HTTP Streaming Response"""

    fields = models.BiologicalDetailing._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names and field.attname:
            field_names.append(field.attname)

    header_row = deepcopy(field_names)
    header_row += [
        "site",
        "site_id",
        "site_name",
        "river_name",
        "arrival_date",
        "departure_date",
        "adipose_condition_display",
        "age_type_display",
    ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    sorted_header = sorted(header_row)
    yield writer.writerow(sorted_header)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]
        data_row += [
            obj.sample.site,
            obj.sample.site_id,
            obj.sample.site.name,
            obj.sample.site.river.name,
            obj.sample.arrival_date,
            obj.sample.departure_date,
            obj.get_adipose_condition_display(),
            obj.get_age_type_display(),
        ]

        sorted_data_row = [x for _, x in sorted(zip(header_row, data_row))]
        yield writer.writerow(sorted_data_row)


def generate_specimen_csv_v1(qs):
    """Returns a generator for an HTTP Streaming Response"""
    header_row = [
        "Site",
        "Year",
        "Month",
        "Day",
        "Time_start",
        "Time_end",
        "Species",
        "TAG_ID",
        "Status",
        "Origin",
        "FL",
        "TotL",
        "Weight",
        "Sex",
        "Smolt age",
        "Scale_ID",
        "JULIAN_DAY",
        "ORDINAL_DAY",
        "First_Tag_location",
        "First_Tag_Day",
        "DAYS_AFTER_RT",
        "FishID",
    ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    for obj in qs:

        first_tag_location = "NA"
        first_tag_day = "NA"
        days_after_rt = "NA"

        if obj.is_recapture:
            if obj.first_tagging:
                first_tag_location = obj.first_tagging.sample.site
                first_tag_day = obj.first_tagging.sample.arrival_date.strftime("%Y-%m-%d")
                days_after_rt = obj.sample.arrival_date.toordinal() - obj.first_tagging.sample.arrival_date.toordinal()
            else:
                first_tag_location = "cannot find record of first tagging"
                first_tag_day = "cannot find record of first tagging"
                days_after_rt = "cannot find record of first tagging"

        data_row = [
            obj.sample.site,
            obj.sample.arrival_date.year,
            obj.sample.arrival_date.month,
            obj.sample.arrival_date.day,
            get_timezone_time(obj.sample.arrival_date).strftime("%H:%M"),
            get_timezone_time(obj.sample.departure_date).strftime("%H:%M"),
            f"{obj.species} ({obj.life_stage})",
            nz(obj.tag_number, "NA"),
            obj.status.code if obj.status else "NA",
            obj.origin.code if obj.origin else "NA",
            obj.fork_length if obj.fork_length else "NA",
            obj.total_length if obj.total_length else "NA",
            nz(obj.weight, "NA"),
            obj.sex.code if obj.sex else "NA",
            nz(obj.river_age, "NA"),
            nz(obj.scale_id_number, "NA"),
            nz(obj.sample.julian_day, "NA"),
            obj.sample.arrival_date.toordinal(),
            first_tag_location,
            first_tag_day,
            days_after_rt,
            obj.id,
        ]
        yield writer.writerow(data_row)


def generate_electro_juv_salmon_report(qs):
    """Returns a generator for an HTTP Streaming Response"""

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    headers = [
        'Year',
        'Month',
        'Day',
        'River',
        'Site',
        'Site type',
        'Full wetted width',
        'Sweep #',
        'Total seconds swept',
    ]

    # get a comprehensive list of life stages
    life_stages = models.LifeStage.objects.filter(specimens__sweep__in=qs, specimens__species__tsn=161996).distinct().order_by("id")
    for ls in life_stages:
        headers.append(f"# of {ls}")

    yield writer.writerow(headers)

    for sweep in qs:
        data_row = [
            sweep.sample.arrival_date.year,
            sweep.sample.arrival_date.month,
            sweep.sample.arrival_date.day,
            sweep.sample.site.river,
            sweep.sample.site.name,
            sweep.sample.ef_sample.get_site_type_display(),
            sweep.sample.ef_sample.full_wetted_area,
            sweep.sweep_number,
            sweep.sweep_time,
        ]
        for ls in life_stages:
            data_row.append(sweep.specimens.filter(life_stage=ls).count())
        yield writer.writerow(data_row)


# RESTIGOUCH OPEN DATA REPORTS

def generate_od_sp_list(qs):
    """
    Generates the data dictionary for open data report version 1
    """

    filename = "species_list.csv"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    # write the header
    header = [
        "common_name_en__nom_commun_en",
        "common_name_en__nom_commun_fr",
        "scientific_name__nom_scientifique",
        "ITIS_TSN",
    ]
    writer.writerow(header)

    for sp in qs:
        writer.writerow([
            sp.common_name_eng,
            sp.common_name_fre,
            sp.scientific_name,
            sp.tsn,
        ])

    return response


def generate_od_summary_by_site_dict(report_name):
    """
    Generates the data dictionary for open data report version 1
    """

    filename = "data_dictionary.csv"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

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

    field_names = [
        "[SP]_abundance",
        "[SP]_avg_fork_length",
        "[SP]_avg_total_length",
        "[SP]_avg_weight",
    ]

    descr_eng = [
        "total abundance of a species for a given site and year",
        "mean fork length (mm) of a species for a given site and year",
        "mean total length (mm) of a species for a given site and year; this is only provided for American eel",
        "mean weight (g) of a species for a given site and year",
    ]
    descr_fra = [
        "Abondance totale d'une espèce pour un site et une année donnés",
        "longueur à la fourche moyenne (mm) d'une espèce pour un site et une année donnés",
        "longueur totale moyenne (mm) d'une espèce pour un site et une année donnés; fourni que pour l'anguille d'Amérique",
        "poids moyen (g) d'une espèce pour un site et une année donnés",
    ]
    for i in range(0, len(field_names)):
        writer.writerow([
            field_names[i],
            descr_eng[i],
            descr_fra[i],
        ])

    return response


def generate_od_summary_by_site_report(qs):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    # we only want to look at sites that caught fish
    qs = qs.filter(specimens__isnull=False).distinct()
    # headers are based on csv provided by GD
    species_list = [models.Species.objects.get(pk=obj["specimens__species"]) for obj in
                    qs.order_by("specimens__species").values("specimens__species").distinct()]

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
        if species.tsn == 161127:  # eel
            addendum = [
                "{}_abundance".format(slugify(species.scientific_name).replace("-", "_")),
                "{}_avg_total_length".format(slugify(species.scientific_name).replace("-", "_")),
                "{}_avg_weight".format(slugify(species.scientific_name).replace("-", "_")),
            ]
        else:
            addendum = [
                "{}_abundance".format(slugify(species.scientific_name).replace("-", "_")),
                "{}_avg_fork_length".format(slugify(species.scientific_name).replace("-", "_")),
                "{}_avg_weight".format(slugify(species.scientific_name).replace("-", "_")),
            ]
        header_row.extend(addendum)

    yield writer.writerow(header_row)

    # let's start by getting a list of samples and years
    sites = [models.RiverSite.objects.get(pk=obj["site"]) for obj in qs.order_by("site").values("site").distinct()]
    years = [obj["season"] for obj in qs.order_by("season").values("season").distinct()]

    for year in years:
        for site in sites:
            qs_year_site = qs.filter(season=year, site=site)

            data_row = [
                year,
                site,
                site.latitude,
                site.longitude,
                floatformat(qs_year_site.aggregate(avg=Avg("rst_sample__air_temp_arrival"))["avg"], 3),
                floatformat(qs_year_site.aggregate(avg=Avg("max_air_temp"))["avg"], 3),
                floatformat(qs_year_site.aggregate(avg=Avg("rst_sample__water_temp_trap_c"))["avg"], 3),
            ]

            for species in species_list:
                specimen_qs = qs_year_site.filter(specimens__species=species).distinct()

                sp_count = specimen_qs.count()

                if species.tsn == 161127:  # eel
                    avg_len = floatformat(specimen_qs.aggregate(avg=Avg("specimens__total_length"))["avg"], 3)
                else:
                    avg_len = floatformat(specimen_qs.aggregate(avg=Avg("specimens__fork_length"))["avg"], 3)

                avg_weight = floatformat(specimen_qs.aggregate(avg=Avg("specimens__weight"))["avg"], 3)

                addendum = [sp_count, avg_len, avg_weight]
                data_row.extend(addendum)

            yield writer.writerow(data_row)


def generate_od_summary_by_site_wms(lang):
    """
    Simple report for web mapping service on FGP
    """
    qs = models.Entry.objects.all()
    filename = "site_summary_report_eng.csv" if lang == 1 else "site_summary_report_fra.csv"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    # headers are based on csv provided by GD
    species_list = [models.Species.objects.get(pk=obj["species"]) for obj in qs.order_by("species").values("species").distinct()]

    select_species_dict = {
        "fish_gr_1": {
            "codes": [1732],
            "eng": "Altantic_salmon_smolts",
            "fra": "de_saumons_atlantiques_saumoneaux",
        },
        "fish_gr_2": {
            "codes": [3410],
            "eng": "American_eels",
            "fra": "d_anguilles_d_Amériques",
        },
        "fish_gr_3": {
            "codes": [140, 150, 151, 152],
            "eng": "lampreys",
            "fra": "de_lamproies",
        },
        "fish_gr_4": {
            "codes": [2621, 2631, 2620, 2630, 2640],
            "eng": "dace",
            "fra": "de_vandoise",
        },

    }

    header_row = [
        'Site_name' if lang == 1 else "Nom_de_site",
        'Site_latitude' if lang == 1 else "Latitude_de_site",
        'Site_longitude' if lang == 1 else "Longitude_de_site",
        'Seasons_in_operation' if lang == 1 else "Saisons_en_opération",
        'List_of_species_caught' if lang == 1 else "Liste_des_espèces_capturées",
        'Total_number_of_fish_caught' if lang == 1 else "Nombre_total_de_poisson_capturées",
        'Mean_annual_number_of_fish_caught' if lang == 1 else "Nombre_annuel_moyen_de_poissons_capturés",
    ]

    for key in select_species_dict:
        if lang == 1:
            header_row.extend([
                'Total_number_of_{}_caught'.format(select_species_dict[key]["eng"]),
                'Mean_annual_number_of_{}_caught'.format(select_species_dict[key]["eng"]),
            ])
        else:
            header_row.extend([
                'Nombre_total_{}_capturées'.format(select_species_dict[key]["fra"]),
                'Nombre_annuel_moyen_{}_capturés'.format(select_species_dict[key]["fra"]),
            ])
    writer.writerow(header_row)

    # lets start by getting a list of samples and years
    # samples = [models.Sample.objects.get(pk=obj["sample"]) for obj in qs.order_by("sample").values("sample").distinct()]
    sites = [models.RiverSite.objects.get(pk=obj["sample__site"]) for obj in qs.order_by("sample__site").values("sample__site").distinct()]

    for site in sites:
        seasons = listrify(
            [obj["sample__season"] for obj in qs.filter(sample__site=site).order_by("sample__season").values("sample__season").distinct()])

        if lang == 1:
            spp_list = listrify([models.Species.objects.get(pk=obj["species"]).common_name_eng for obj in
                                 qs.filter(sample__site=site).order_by("species").values("species").distinct()])
        else:
            spp_list = listrify([models.Species.objects.get(pk=obj["species"]).common_name_fre for obj in
                                 qs.filter(sample__site=site).order_by("species").values("species").distinct()])
        total_freq = qs.filter(sample__site=site, ).values("frequency").order_by("frequency").aggregate(
            dsum=Sum("frequency"))["dsum"]
        avg_freq = floatformat(int(total_freq) / len(seasons.split(",")), 2)

        data_row = [
            site,
            site.latitude_n,
            site.longitude_w,
            seasons,
            spp_list,
            total_freq,
            avg_freq,
        ]

        for key in select_species_dict:
            freq_sum = qs.filter(
                sample__site=site,
                species__code__in=select_species_dict[key]["codes"]
            ).values("frequency").order_by("frequency").aggregate(
                dsum=Sum("frequency"))["dsum"]
            freq_avg = floatformat(int(freq_sum) / len(seasons.split(",")), 2)

            data_row.extend([
                freq_sum,
                freq_avg,
            ])

        writer.writerow(data_row)

    return response
