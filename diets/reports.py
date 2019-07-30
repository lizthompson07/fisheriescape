import math

import unicodecsv as csv
from django.http import HttpResponse
from django.template.defaultfilters import yesno
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from lib.functions.custom_functions import nz
from . import models
import numpy as np


def generate_progress_report(year):
    # create instance of mission:
    qs = models.Sample.objects.filter(season=year)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="herring_progress_report_{}.csv"'.format(year)
    writer = csv.writer(response)

    # write the header information
    writer.writerow(['{} Herring Progress Report'.format(year), "", "", "", "", "",
                     'Report generated on {}'.format(timezone.now().strftime('%Y-%m-%d %H:%M')), ])

    # write the header for the bottle table
    writer.writerow(["", ])

    writer.writerow([
        "Season",
        "Sample no.",
        "Type",
        "Sample date",
        "Sampler's reference no.",
        "Sampler Name",
        "Length frequencies collected",
        "Fish preserved",
        "Lab processing",
        "Otoliths processing",
    ])

    for sample in qs:
        if sample.fish_details.count():
            if sample.fish_details.last().lab_processed_date:
                lab_processed_date = sample.fish_details.last().lab_processed_date.strftime('%Y-%m-%d')
            else:
                lab_processed_date = ""
            if sample.fish_details.last().otolith_processed_date:
                otolith_processed_date = sample.fish_details.last().otolith_processed_date.strftime('%Y-%m-%d')
            else:
                otolith_processed_date = ""
        else:
            lab_processed_date = ""
            otolith_processed_date = ""

        writer.writerow(
            [
                sample.season,
                sample.id,
                sample.get_type_display(),
                sample.sample_date.strftime('%Y-%m-%d'),
                sample.sampler_ref_number,
                sample.sampler,
                yesno(sample.length_frequency_objects.count()),
                sample.total_fish_preserved,
                lab_processed_date,
                otolith_processed_date,
            ])

    return response





def export_data(year, cruise):
    """
    Generic data export
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