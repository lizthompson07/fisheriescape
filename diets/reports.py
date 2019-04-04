import math

import unicodecsv as csv
from django.http import HttpResponse
from django.template.defaultfilters import yesno
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from lib.functions.nz import nz
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

