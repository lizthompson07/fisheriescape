from django.utils import timezone

from . import models

import os
import csv


def import_old_data():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "diet_import.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        for row in my_csv:

            # first get the predator
            my_pred, created = models.Predator.objects.get_or_create(
                old_seq_num=row["SeqNoUhl"],
                species_id=row["Predator"],
            )

            # if the predator is being created, populate it with stuff
            if created:
                my_pred.cruise_id = row["cruise_id"]
                my_pred.processing_date = timezone.datetime(row["year_pro"],row["month_pro"], row["day_pro"])
                my_pred.set = row["Set"]
                my_pred.fish_number = row["FishNo"]
                my_pred.somatic_length_cm = row["PredLen"]
                my_pred.stomach_wt_g = row["StomWt"]
                my_pred.comments = row["survey_comment"]
                my_pred.stratum = row["Strat"]
                my_pred.date_last_modified = timezone.now()

            # next get the prey item
            my_pray, created = models.Prey.objects.get_or_create(
                old_seq_num=row["SeqNoUhl"],
                species_id=row["Predator"],
            )

            # if the predator is being created, populate it with stuff
            if created:
                my_pred.cruise_id = row["cruise_id"]
                my_pred.processing_date = timezone.datetime(row["year_pro"], row["month_pro"], row["day_pro"])
                my_pred.set = row["Set"]
                my_pred.fish_number = row["FishNo"]
                my_pred.somatic_length_cm = row["PredLen"]
                my_pred.stomach_wt_g = row["StomWt"]
                my_pred.comments = row["survey_comment"]
                my_pred.stratum = row["Strat"]
                my_pred.date_last_modified = timezone.now()

            # samplers

            my_obs, created = models.SpeciesObservations.objects.get_or_create(sample_id=int(row["sample_id"]),
                                                                               species_id=int(row["species_id"]))
