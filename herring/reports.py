import unicodecsv as csv
from django.http import HttpResponse
from django.utils import timezone
from . import models

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
                sample.total_fish_preserved,
                lab_processed_date,
                otolith_processed_date,
            ])

    return response

def generate_fish_detail_report(request, year):
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
            otolith_sampler = "{} {}".format(fish_detail.otolith_sampler.first_name, fish_detail.otolith_sampler.last_name)
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
