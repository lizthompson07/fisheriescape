import math

import unicodecsv as csv
from django.http import HttpResponse
from django.template.defaultfilters import yesno
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from lib.functions.custom_functions import nz
from lib.functions.verbose_field_name import verbose_field_name
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


def generate_sample_report(year):
    # create instance of mission:
    qs = models.Sample.objects.filter(season=year)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="herring_sample_report_{}.csv"'.format(year)
    writer = csv.writer(response)

    writer.writerow([
        verbose_field_name(qs.first(), "id"),
        verbose_field_name(qs.first(), 'season'),
        verbose_field_name(qs.first(), 'type'),
        verbose_field_name(qs.first(), 'sample_date'),
        verbose_field_name(qs.first(), 'sampler_ref_number'),
        verbose_field_name(qs.first(), 'sampler'),
        verbose_field_name(qs.first(), 'port'),
        verbose_field_name(qs.first(), 'district'),
        verbose_field_name(qs.first(), 'survey_id'),
        verbose_field_name(qs.first(), 'latitude_n'),
        verbose_field_name(qs.first(), 'longitude_w'),
        verbose_field_name(qs.first(), 'fishing_area'),
        verbose_field_name(qs.first(), 'gear'),
        verbose_field_name(qs.first(), 'experimental_net_used', ),
        verbose_field_name(qs.first(), 'vessel_cfvn'),
        verbose_field_name(qs.first(), 'mesh_size'),
        verbose_field_name(qs.first(), 'total_fish_measured'),
        "length-frequency counts",
        verbose_field_name(qs.first(), 'total_fish_preserved'),
        verbose_field_name(qs.first(), 'catch_weight_lbs'),
        verbose_field_name(qs.first(), 'sample_weight_lbs'),
        verbose_field_name(qs.first(), 'remarks'),
    ])

    for sample in qs:
        if sample.sample_date:
            sample_date = sample.sample_date.strftime('%Y-%m-%d')
        else:
            sample_date = None

        if sample.port:
            district = "{}{}".format(sample.port.province_code, sample.port.district_code)
        else:
            district = None

        writer.writerow(
            [
                sample.id,
                sample.season,
                sample.get_type_display(),
                sample_date,
                sample.sampler_ref_number,
                str(sample.sampler),
                str(sample.port),
                district,
                sample.survey_id,
                sample.latitude_n,
                sample.longitude_w,
                str(sample.fishing_area),
                str(sample.gear),
                sample.experimental_net_used,
                sample.vessel_cfvn,
                str(sample.mesh_size),
                sample.total_fish_measured,
                sample.lf_count,
                sample.total_fish_preserved,
                sample.catch_weight_lbs,
                sample.sample_weight_lbs,
                sample.remarks,
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
    sample_list = [s for s in models.Sample.objects.filter(season=year).order_by("sample_date") if s.length_frequencies.count() > 0]

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

            # we will have to turn this into a fixed width
            padding_lengths = [5, 2, 2, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, ]

            writer.writerow(
                [
                    str(sample.id).rjust(padding_lengths[0]),
                    str(sample.sample_date.day).rjust(padding_lengths[1]),
                    str(sample.sample_date.month).rjust(padding_lengths[2]),
                    str(sample.sample_date.year).rjust(padding_lengths[3]),
                    str(int(row[0])).rjust(padding_lengths[4]),
                    str(length_list[0]).rjust(padding_lengths[5]),
                    str(length_list[1]).rjust(padding_lengths[6]),
                    str(length_list[2]).rjust(padding_lengths[7]),
                    str(length_list[3]).rjust(padding_lengths[8]),
                    str(length_list[4]).rjust(padding_lengths[9]),
                    str(length_list[5]).rjust(padding_lengths[10]),
                    str(length_list[6]).rjust(padding_lengths[11]),
                    str(length_list[7]).rjust(padding_lengths[12]),
                    str(length_list[8]).rjust(padding_lengths[13]),
                    str(length_list[9]).rjust(padding_lengths[14]),
                ])

    return response


def generate_hlog(year):
    # grab a list of all samples for the year
    sample_list = [s for s in models.Sample.objects.filter(season=year).order_by("sample_date")]

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hlog{}.csv"'.format(year)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    # these files have no headers so we jump straight into the date
    # here is where things get tricky.. each row should consist of 10 columns of data + metadata (5 cols)
    # lets define a few custom functions:

    # we will have to turn this into a fixed width
    padding_lengths = [5, 2, 2, 4, 20, 15, 6, 3, 3, 3, 3, 20, 4, 4, 6, 6, 6, 2, 8, 3, 3, 10, 15, 85, 4, 4, 7, 7]

    for sample in sample_list:

        # a) sample
        col_a = str(sample.id).rjust(padding_lengths[0])

        # b) day
        col_b = str(nz(sample.sample_date.day, "")).rjust(padding_lengths[1])

        # c) month
        col_c = str(nz(sample.sample_date.month, "")).rjust(padding_lengths[2])

        # d) year
        col_d = str(nz(sample.sample_date.year, "")).rjust(padding_lengths[3])

        # e) maps to PORT_NAME but will also contain survey ID from new database
        if sample.survey_id:
            my_var = sample.survey_id
        elif sample.port_id:
            if sample.port.alias_wharf_name:
                my_var = sample.port.alias_wharf_name
            else:
                my_var = "UNKNOWN"

        else:
            my_var = ""
        col_e = str(my_var).rjust(padding_lengths[4])

        # f) sampler name (text)
        if sample.sampler:
            # if there is a missing first or last name
            if not sample.sampler.first_name or not sample.sampler.last_name:
                sampler = "{}{}".format(nz(sample.sampler.first_name, ""), nz(sample.sampler.last_name, ""))
            else:
                sampler = "{}. {}".format(sample.sampler.first_name.upper()[:1], sample.sampler.last_name.upper())
        else:
            sampler = ""
        col_f = str(sampler).rjust(padding_lengths[5])

        # g) sampler's ref number
        col_g = str(nz(sample.sampler_ref_number, "")).rjust(padding_lengths[6])

        # h) number measured??
        col_h = str(nz(sample.total_fish_measured, "")).rjust(padding_lengths[7])

        # i) number kept
        col_i = str(nz(sample.total_fish_preserved, "")).rjust(padding_lengths[8])

        # j) NAFO code
        if sample.fishing_area:
            nafo_code = sample.fishing_area.nafo_area_code
        else:
            nafo_code = ""
        col_j = str(nafo_code).rjust(padding_lengths[9])

        # k) district id; maps to PORT_CODE in oracle db ** can also be research code
        # if it is experimental, we assign a research code
        if sample.experimental_net_used:
            # if gear is OTM, rc = 901
            if sample.gear_id == 26:
                my_var = 901
            # if gear is OTB, rc = 905
            elif sample.gear_id == 25:
                my_var = 905
            # if gear is GNS, rc = 908
            elif sample.gear_id == 2:
                my_var = 908
            # otherwise default to 908.
            else:
                my_var = 999

        # if there is a port, we give a district number (i.e. province_code + district_code
        else:
            if sample.port:
                my_var = "{}{}".format(sample.port.province_code, sample.port.district_code)
            else:
                my_var = ""
        col_k = str(nz(my_var, "")).rjust(padding_lengths[10])

        # l) cfvn
        col_l = str(nz(sample.vessel_cfvn, "")).rjust(padding_lengths[11])

        # m) gear code (str)
        if sample.gear:
            gear_code = sample.gear.gear_code
            if sample.experimental_net_used:
                gear_code = gear_code + "*"
        else:
            gear_code = ""
        col_m = str(gear_code).rjust(padding_lengths[12])

        # n) mesh size (float)
        if sample.mesh_size:
            mesh_size = "{:.2f}".format(sample.mesh_size.size_inches_decimal)
        else:
            mesh_size = ""
        col_n = str(mesh_size).rjust(padding_lengths[13])

        # o) lat
        if sample.latitude_n:
            my_var = sample.latitude_n[:6]
        else:
            my_var = ""
        col_o = str(nz(my_var, "")).rjust(padding_lengths[14])

        # p) long
        if sample.longitude_w:
            my_var = sample.longitude_w[:6]
        else:
            my_var = ""
        col_p = str(nz(my_var, "")).rjust(padding_lengths[15])

        # q) landed wt.
        if sample.catch_weight_lbs:
            catch_wt = int(sample.catch_weight_lbs)
        else:
            catch_wt = ""
        col_q = str(catch_wt).rjust(padding_lengths[16])

        # r) sampling protocol
        if sample.type == 2:  # sea sample
            protocol = 8
        else:  # port sample
            if sample.experimental_net_used:
                # mesh selectivity
                protocol = 2
            else:
                # vanilla port sampling
                protocol = 1
        col_r = str(protocol).rjust(padding_lengths[17])

        # s) blank
        col_s = str("").rjust(padding_lengths[18])

        # t) length frequency bins
        col_t = str(0.5).rjust(padding_lengths[19])

        # u) number processed
        col_u = str(nz(sample.total_fish_preserved, "")).rjust(padding_lengths[20])

        # v) date processed
        col_v = str("").rjust(padding_lengths[21])

        # w) ager name
        col_w = str("").rjust(padding_lengths[22])

        # x) comment
        col_x = str("").rjust(padding_lengths[23])

        # y) blank
        col_y = str("").rjust(padding_lengths[24])

        # z) maps to WHARF_CODE in oracle db
        if sample.port:
            if sample.port.alias_wharf_id:
                my_var = sample.port.alias_wharf_id
            else:
                my_var = ""
        else:
            my_var = ""
        col_z = str(my_var).rjust(padding_lengths[25])

        # aa) blank
        col_aa = str("").rjust(padding_lengths[26])

        # ab) blank
        col_ab = str("").rjust(padding_lengths[27])

        writer.writerow(
            [
                col_a,
                col_b,
                col_c,
                col_d,
                col_e,
                col_f,
                col_g,
                col_h,
                col_i,
                col_j,
                col_k,
                col_l,
                col_m,
                col_n,
                col_o,
                col_p,
                col_q,
                col_r,
                col_s,
                col_t,
                col_u,
                col_v,
                col_w,
                col_x,
                col_y,
                col_z,
                col_aa,
                col_ab,
            ])

    return response


def generate_hdet(year):
    # grab a list of all fish details for the year, ordered by sample then fish number
    fish_list = [f for f in models.FishDetail.objects.filter(sample__season=year).order_by("sample__sample_date", "fish_number")]

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hdet{}.csv"'.format(year)
    writer = csv.writer(response)

    # these files have no headers so we jump straight into the date
    # here is where things get tricky.. each row should consist of 10 columns of data + metadata (5 cols)
    # lets define a few custom functions:

    for fish in fish_list:
        # only do this if the fish was fully processed in the lab!
        if fish.lab_processed_date:

            # sample, day, month, year, fish_number,
            # fishlength, fishweight, sex (M,F,I),
            # maturity, gonadweight, otolith_season, annulus_count


            if fish.sex:
                sex = fish.sex.oracle_code
            else:
                sex = ""

            if fish.maturity:
                # the other database uses 0 as unknown, as oppposed to 9
                if fish.maturity.id == 9:
                    maturity = 0
                else:
                    maturity = fish.maturity.id
            else:
                maturity = ""

            if fish.otolith_season:
                os = fish.otolith_season.oracle_code
            else:
                os = ""

            if fish.annulus_count == -99 or fish.annulus_count is None:
                annulus_count = ""
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
                    "{:.1f}".format(fish.gonad_weight).rjust(padding_lengths[9]),
                    str(os).ljust(padding_lengths[10]),
                    str(annulus_count).rjust(padding_lengths[11]),
                ])

    return response
