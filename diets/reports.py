import math

import unicodecsv as csv
from django.http import HttpResponse
from django.template.defaultfilters import yesno
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from lib.functions.custom_functions import nz, listrify
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


def export_data(year, cruise, spp):
    """
    Generic data export
    """

    filename = "diet_db_export_{}.csv".format(timezone.now().strftime("%Y-%m-%d"))
    qs = models.Prey.objects.all()

    if year != "None":
        qs = qs.filter(predator__processing_date__year=year)

    if cruise != "None":
        qs = qs.filter(predator__cruise_id=cruise)

    if spp != "None":
        qs = qs.filter(predator__species_id__in=spp.split(","))

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    header_row = [

        # from predator
        'cruise_name',
        'cruise_number',
        'cruise_year',
        'set',
        'fish_number',
        'samplers',
        'processing_date',
        'processing_year',
        'predator_id',
        'stomach_id',
        'predator_species_code',
        'predator_species_common_name',
        'predator_species_latin_name',
        'somatic_length_cm',
        'stomach_wt_g',
        'content_wt_g',
        'predator_comments',

        # from prey
        'prey_id',
        'prey_species_code',
        'prey_species_common_name',
        'prey_species_latin_name',
        'digestion_level_id',
        'digestion_level_description',
        'somatic_length_mm',
        'length_comment',
        'number_of_prey',
        'somatic_wt_g',
        'prey_comments',

    ]
    writer.writerow(header_row)

    for prey in qs:
        writer.writerow([
            # from predator
            prey.predator.cruise.mission_name if prey.predator.cruise else None,
            prey.predator.cruise.mission_number if prey.predator.cruise else None,
            prey.predator.cruise.season if prey.predator.cruise else None,
            prey.predator.set,
            prey.predator.fish_number,
            listrify([obj for obj in prey.predator.samplers.all()]),
            prey.predator.processing_date.strftime('%Y-%m-%d') if prey.predator.processing_date else None,
            prey.predator.processing_date.year if prey.predator.processing_date else None,
            prey.predator.id,
            prey.predator.stomach_id,
            prey.predator.species.id if prey.predator.species else None,
            prey.predator.species.common_name_eng if prey.predator.species else None,
            prey.predator.species.scientific_name if prey.predator.species else None,
            prey.predator.somatic_length_cm,
            prey.predator.stomach_wt_g,
            prey.predator.content_wt_g,
            prey.predator.comments,

            # from prey
            prey.id,
            prey.species.id if prey.species else None,
            prey.species.common_name_eng if prey.species else None,
            prey.species.scientific_name if prey.species else None,
            prey.digestion_level.id if prey.digestion_level else None,
            prey.digestion_level.level if prey.digestion_level else None,
            prey.somatic_length_mm,
            prey.length_comment,
            prey.number_of_prey,
            prey.somatic_wt_g,
            prey.comments,
        ])


    return response
