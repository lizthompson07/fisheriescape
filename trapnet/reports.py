from copy import deepcopy

import unicodecsv as csv
from django.db.models import Sum, Avg
from django.http import HttpResponse
from django.template.defaultfilters import floatformat

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

    header_row = deepcopy(field_names)
    header_row += [
        "sample_type_display",
        "precipitation_category_display",
        "wind_speed_display",
        "wind_direction_display",
        "didymo_display",
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
                "full_wetted_width"
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

    for obj in qs:
        sub_obj = obj.get_sub_obj()
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]
        data_row += [
            obj.get_sample_type_display(),
            obj.get_precipitation_category_display(),
            obj.get_wind_speed_display(),
            obj.get_wind_direction_display(),
            obj.get_didymo_display(),
        ]
        data_row += [str(nz(getattr(sub_obj, field), "")).encode("utf-8").decode('utf-8') for field in sub_field_names]
        if is_ef:
            data_row += [
                sub_obj.get_site_type_display(),
                sub_obj.get_seine_type_display(),
                sub_obj.get_electrofisher_pulse_type_display(),
                sub_obj.get_full_wetted_width(show_errors=False),
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

    fields = models.Sweep._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)

    field_names.sort()
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(field_names)

    for obj in qs:
        data_row = [str(nz(getattr(obj, field), "")).encode("utf-8").decode('utf-8') for field in field_names]
        yield writer.writerow(data_row)





def generate_specimen_csv(qs, sample_type):
    """Returns a generator for an HTTP Streaming Response"""

    fields = models.Specimen._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)
    field_names.remove("sweep")
    field_names.remove("sweep_id")

    header_row = deepcopy(field_names)
    header_row += [
        "site",
        "site_id",
        "arrival_date",
        "departure_date",
        "adipose_condition_display",
        "age_type_display",
        "smart_river_age",
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
            "full_wetted_width",
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
            obj.sample.arrival_date,
            obj.sample.departure_date,
            obj.get_adipose_condition_display(),
            obj.get_age_type_display(),
            obj.smart_river_age,
        ]

        if is_ef:
            sub_obj = obj.sample.get_sub_obj()
            data_row += [
                obj.sweep_id,
                obj.sweep.sweep_number,
                obj.sweep.sweep_time,
                sub_obj.get_full_wetted_width(show_errors=False),
            ]

        sorted_data_row = [x for _, x in sorted(zip(header_row, data_row))]
        yield writer.writerow(sorted_data_row)

def generate_biological_detailing_csv(qs):
    """Returns a generator for an HTTP Streaming Response"""

    fields = models.BiologicalDetailing._meta.fields
    field_names = [field.name for field in fields]

    # add any FKs
    for field in fields:
        if field.attname not in field_names:
            field_names.append(field.attname)

    header_row = deepcopy(field_names)
    header_row += [
        "site",
        "site_id",
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
            sweep.sample.ef_sample.get_full_wetted_width(False),
            sweep.sweep_number,
            sweep.sweep_time,
        ]
        for ls in life_stages:
            data_row.append(sweep.specimens.filter(life_stage=ls).count())
        yield writer.writerow(data_row)



def generate_spp_list():
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


def generate_open_data_ver_1_data_dictionary():
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
        "[SP_CODE]_abundance",
        "[SP_CODE]_avg_fork_length",
        "[SP_CODE]_avg_total_length",
        "[SP_CODE]_avg_weight",
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


def generate_open_data_ver_1_report(year, sites):
    """
    This is a view designed for FGP / open maps view. The resulting csv will summarize data per site per year

    :param year: int
    :param sites: list of river site PKs
    :return: http response
    """

    # It is important that we remove any samples taken at MAtapedia River since these data do not belong to us.
    if year != "None":
        qs = models.Entry.objects.filter(sample__season=year).all()
        filename = "open_data_ver1_report_{}.csv".format(year)
    else:
        qs = models.Entry.objects.all().all()
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


def generate_open_data_ver_1_wms_report(lang):
    """
    Simple report for web mapping service on FGP
    """
    # It is important that we remove any samples taken at MAtapedia River since these data do not belong to us.
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
