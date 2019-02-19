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


def generate_fish_detail_report(year):
    # create instance of mission:
    qs = models.FishDetail.objects.filter(sample__season=year)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="herring_fish_detail_report_{}.csv"'.format(year)
    writer = csv.writer(response)

    # write the header information
    # writer.writerow(['{} Fish Detail Export'.format(year), "", "", "", "", "",
    #                  'Report generated on {}'.format(timezone.now().strftime('%Y-%m-%d %H:%M')), ])

    # write the header for the bottle table
    # writer.writerow(["", ])

    writer.writerow([
        'sample',
        'season',
        'sample_type',
        'sample_date',
        'sampler_ref_number',
        'sampler',
        'district',
        'survey_id',
        'latitude_n',
        'longitude_w',
        'fishing_area',
        'gear',
        'experimental_net_used',
        'vessel_cfvn',
        'mesh_size',
        'sample_remarks',
        'fish_uid',
        'fish_number',
        'fish_length',
        'fish_weight',
        'sex',
        'maturity',
        'gonad_weight',
        'parasite',
        'lab_sampler',
        'otolith_sampler',
        'lab_processed_date',
        'annulus_count',
        'otolith_season',
        'otolith_image_remote_filepath',
        'otolith_processed_date',
    ])

    for fish_detail in qs:
        if fish_detail.sample.sampler:
            sampler = "{} {}".format(fish_detail.sample.sampler.first_name, fish_detail.sample.sampler.last_name)
        else:
            sampler = None

        if fish_detail.lab_sampler:
            lab_sampler = "{} {}".format(fish_detail.lab_sampler.first_name, fish_detail.lab_sampler.last_name)
        else:
            lab_sampler = None

        if fish_detail.otolith_sampler:
            otolith_sampler = "{} {}".format(fish_detail.otolith_sampler.first_name,
                                             fish_detail.otolith_sampler.last_name)
        else:
            otolith_sampler = None

        if fish_detail.sample.sample_date:
            sample_date = fish_detail.sample.sample_date.strftime('%Y-%m-%d')
        else:
            sample_date = None

        if fish_detail.lab_processed_date:
            lab_processed_date = fish_detail.lab_processed_date.strftime('%Y-%m-%d')
        else:
            lab_processed_date = None

        if fish_detail.otolith_processed_date:
            otolith_processed_date = fish_detail.otolith_processed_date.strftime('%Y-%m-%d')
        else:
            otolith_processed_date = None

        if fish_detail.sample.district:
            district = "{}{}".format(fish_detail.sample.district.province_id, fish_detail.sample.district.district_id)
        else:
            district = None

        writer.writerow(
            [
                fish_detail.sample.id,
                fish_detail.sample.season,
                fish_detail.sample.get_type_display(),
                sample_date,
                fish_detail.sample.sampler_ref_number,
                sampler,
                district,
                fish_detail.sample.survey_id,
                fish_detail.sample.latitude_n,
                fish_detail.sample.longitude_w,
                str(fish_detail.sample.fishing_area),
                str(fish_detail.sample.gear),
                fish_detail.sample.experimental_net_used,
                fish_detail.sample.vessel_cfvn,
                str(fish_detail.sample.mesh_size),
                fish_detail.sample.remarks,
                fish_detail.id,
                fish_detail.fish_number,
                fish_detail.fish_length,
                fish_detail.fish_weight,
                str(fish_detail.sex),
                str(fish_detail.maturity),
                fish_detail.gonad_weight,
                fish_detail.parasite,
                lab_sampler,
                otolith_sampler,
                lab_processed_date,
                fish_detail.annulus_count,
                fish_detail.otolith_season,
                fish_detail.otolith_image_remote_filepath,
                otolith_processed_date,
            ])

    return response


def generate_hlen(year):
    # grab a list of samples for which there are length frequencies
    sample_list = [s for s in models.Sample.objects.filter(season=year) if s.length_frequencies.count() > 0]

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hlen{}.csv"'.format(year)
    writer = csv.writer(response)

    # these files have no headers so we jump straight into the date
    # here is where things get tricky.. each row should consist of 10 columns of data + metadata (5 cols)
    # lets define a few custom functions:

    def round_down(num, divisor):
        ''' round down to the nearest base '''
        return num - (num % divisor)

    def round_up(num, divisor):
        ''' round down to the nearest base '''
        return num - (num % divisor) + divisor

    for sample in sample_list:

        # get the length frequencies for the sample
        lfs = sample.length_frequency_objects.all().order_by("length_bin__bin_length_cm")
        # get the max and min bin lengths rounded up and down, respectively
        min_length = round_down(lfs.first().length_bin.bin_length_cm, 5)
        max_length = round_up(lfs.last().length_bin.bin_length_cm, 5)
        my_array = np.arange(min_length, max_length, 0.5).reshape(
            (-1, 10))  # the minus -1 allows numpy to find the appropriate number of rows

        # now, for each row of this array, we will write a new column
        for row in my_array:
            length_list = []
            for len in row:
                try:
                    # if length exists for that sample, send in the recorded count
                    length_list.append(models.LengthFrequency.objects.get(sample=sample, length_bin=float(len)).count)
                except ObjectDoesNotExist:
                    # otherwise mark a zero value
                    length_list.append(0)

            writer.writerow(
                [
                    sample.id,
                    sample.sample_date.day,
                    sample.sample_date.month,
                    sample.sample_date.year,
                    int(row[0]),
                    length_list[0],
                    length_list[1],
                    length_list[2],
                    length_list[3],
                    length_list[4],
                    length_list[5],
                    length_list[6],
                    length_list[7],
                    length_list[8],
                    length_list[9],
                ])

    return response


def generate_hlog(year):
    # grab a list of all samples for the year
    sample_list = [s for s in models.Sample.objects.filter(season=year).order_by("id")]

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hlog{}.csv"'.format(year)
    writer = csv.writer(response)

    # these files have no headers so we jump straight into the date
    # here is where things get tricky.. each row should consist of 10 columns of data + metadata (5 cols)
    # lets define a few custom functions:

    for sample in sample_list:
        # sample
        # day
        # month
        # year
        # maps to PORT_NAME but will also contain survey ID from new database
        # sampler name (text)
        # sampler's ref number
        # number measured??
        # number kept
        # NAFO code
        # district id; maps to PORT_CODE in oracle db
        # cfvn
        # gear code (str)
        # mesh size (float)
        # lat
        # long
        # landed wt.
        # number measured per ½ cm
        # blank
        # length frequency bins
        # number processed
        # date processed
        # ager name
        # comment
        # blank
        # maps to WHARF_CODE in oracle db
        # blank

        if sample.sampler:
            # if there is a missing first or last name
            if not sample.sampler.first_name or not sample.sampler.last_name:
                sampler = "{}{}".format(nz(sample.sampler.first_name, ""), nz(sample.sampler.last_name, ""))
            else:
                sampler = "{}. {}".format(sample.sampler.first_name.upper()[:1], sample.sampler.last_name.upper())
        else:
            sampler = None

        if sample.survey_id:
            survey_id = sample.survey_id
        else:
            survey_id = None

        if sample.fishing_area:
            nafo_code = sample.fishing_area.nafo_area_code

        else:
            nafo_code = None

        if sample.gear:
            gear_code = sample.gear.gear_code
            if sample.experimental_net_used:
                gear_code = gear_code + "*"
        else:
            gear_code = None

        if sample.mesh_size:
            mesh_size = sample.mesh_size.size_inches_decimal
        else:
            mesh_size = None

        # based on a discussion with Francois Turcotte, we will try leaving this blank
        if sample.type == 2:  # sea sample
            protocol = 8
        else:  # port sample
            if sample.experimental_net_used:  # sea sample
                protocol = 2
            else:
                protocol = 1

        writer.writerow(
            [
                sample.id,
                sample.sample_date.day,
                sample.sample_date.month,
                sample.sample_date.year,
                survey_id,
                sampler,
                sample.sampler_ref_number,
                sample.total_fish_measured,
                sample.total_fish_preserved,
                nafo_code,
                sample.district_id,
                sample.vessel_cfvn,
                gear_code,
                mesh_size,
                sample.latitude_n,
                sample.longitude_w,
                sample.catch_weight_lbs,
                protocol,
                None,
                0.5,
                sample.total_fish_preserved,
                None,
                None,
                None,
                # sample.remarks,
                None,
                None,
                None,
            ])

    return response


def generate_hdet(year):
    # grab a list of all fish details for the year, ordered by sample then fish number
    fish_list = [f for f in models.FishDetail.objects.filter(sample__season=year).order_by("sample_id", "fish_number")]

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hdet{}.csv"'.format(year)
    writer = csv.writer(response)

    # these files have no headers so we jump straight into the date
    # here is where things get tricky.. each row should consist of 10 columns of data + metadata (5 cols)
    # lets define a few custom functions:

    for fish in fish_list:
        # sample, day, month, year, fish_number,
        # fishlength, fishweight, sex (M,F,I),
        # maturity, gonadweight, otolith_season, annulus_count

        if fish.sex:
            sex = fish.sex.oracle_code
        else:
            sex = None

        if fish.maturity:
            # the other database uses 0 as unknown, as oppposed to 9
            if fish.maturity.id == 9:
                maturity = 0
            else:
                maturity = fish.maturity.id
        else:
            maturity = None

        if fish.otolith_season:
            os = fish.otolith_season.oracle_code
        else:
            os = None

        if fish.annulus_count == -99:
            annulus_count = None
        else:
            annulus_count = fish.annulus_count

        # we will have to turn this into a fixed width
        padding_lengths = [5, 2, 2, 4, 3, 3, 3, 1, 1, 5, 3, 2]

        writer.writerow(
            [
                str(fish.sample.id).rjust(padding_lengths[0]),
                str(fish.sample.sample_date.day).rjust(padding_lengths[1]),
                str(fish.sample.sample_date.month).rjust(padding_lengths[2]),
                str(fish.sample.sample_date.year).rjust(padding_lengths[3]),
                str(fish.fish_number).rjust(padding_lengths[4]),
                # must be cast to int
                str(int(math.ceil(fish.fish_length))).rjust(padding_lengths[5]),
                # must be cast to int
                str(int(math.ceil(fish.fish_weight))).rjust(padding_lengths[6]),
                str(sex).rjust(padding_lengths[7]),
                str(maturity).rjust(padding_lengths[8]),
                str(fish.gonad_weight).rjust(padding_lengths[9]),
                str(os).rjust(padding_lengths[10]),
                str(annulus_count).rjust(padding_lengths[11]),
            ])

    return response
