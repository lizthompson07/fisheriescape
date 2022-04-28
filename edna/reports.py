import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from edna import models


def generate_pcr_batch_csv(pk):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pcr_batch_{pk}.csv"'
    writer = csv.writer(response)
    batch = get_object_or_404(models.PCRBatch, pk=pk)

    writer.writerow(['batch_id', batch.id])
    writer.writerow(['year', batch.datetime.year])
    writer.writerow(['month', batch.datetime.month])
    writer.writerow(['day', batch.datetime.day])
    writer.writerow(['hour', batch.datetime.hour])
    writer.writerow(['minute', batch.datetime.minute])
    writer.writerow(['comments', batch.comments])
    writer.writerow(['plate_id', batch.plate_id])
    writer.writerow(['machine_number', batch.machine_number])
    writer.writerow(['run_program', batch.run_program])
    writer.writerow([])
    writer.writerow([
        'plate_well',
        'extract',
        'extraction_number',
        'master_mix',
        'assay',
        'threshold',
        'ct',
        'comments',
    ])

    pcr_assays = models.PCRAssay.objects.filter(pcr__pcr_batch=batch)

    for pcr_assay in pcr_assays:
        writer.writerow([
            pcr_assay.pcr.plate_well,
            pcr_assay.pcr.extract,
            pcr_assay.pcr.extract.extraction_number if pcr_assay.pcr.extract else "",
            pcr_assay.pcr.master_mix,
            pcr_assay.assay,
            pcr_assay.threshold,
            pcr_assay.ct,
            pcr_assay.comments,
        ])

    #
    # for sample in sample_list:
    #
    #     # get the length frequencies for the sample
    #     lfs = sample.length_frequency_objects.all().order_by("length_bin__bin_length_cm")
    #     # get the max and min bin lengths rounded up and down, respectively
    #     min_length = round_down(lfs.first().length_bin.bin_length_cm, 5)
    #     max_length = round_up(lfs.last().length_bin.bin_length_cm, 5)
    #     my_array = np.arange(min_length, max_length, 0.5).reshape(
    #         (-1, 10))  # the minus -1 allows numpy to find the appropriate number of rows
    #
    #     # now, for each row of this array, we will write a new column
    #     for row in my_array:
    #         length_list = []
    #         for len in row:
    #             try:
    #                 # if length exists for that sample, send in the recorded count
    #                 length_list.append(models.LengthFrequency.objects.get(sample=sample, length_bin=float(len)).count)
    #             except ObjectDoesNotExist:
    #                 # otherwise mark a zero value
    #                 length_list.append(0)
    #
    #         # we will have to turn this into a fixed width
    #         padding_lengths = [5, 2, 2, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, ]
    #
    #         writer.writerow(
    #             [
    #                 str(sample.id).rjust(padding_lengths[0]),
    #                 str(sample.sample_date.day).rjust(padding_lengths[1]),
    #                 str(sample.sample_date.month).rjust(padding_lengths[2]),
    #                 str(sample.sample_date.year).rjust(padding_lengths[3]),
    #                 str(int(row[0])).rjust(padding_lengths[4]),
    #                 str(length_list[0]).rjust(padding_lengths[5]),
    #                 str(length_list[1]).rjust(padding_lengths[6]),
    #                 str(length_list[2]).rjust(padding_lengths[7]),
    #                 str(length_list[3]).rjust(padding_lengths[8]),
    #                 str(length_list[4]).rjust(padding_lengths[9]),
    #                 str(length_list[5]).rjust(padding_lengths[10]),
    #                 str(length_list[6]).rjust(padding_lengths[11]),
    #                 str(length_list[7]).rjust(padding_lengths[12]),
    #                 str(length_list[8]).rjust(padding_lengths[13]),
    #                 str(length_list[9]).rjust(padding_lengths[14]),
    #             ])

    return response
