from django.utils import timezone

from lib.templatetags.custom_filters import nz
from . import models

import os
import csv


def import_old_data():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "diet_import.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        for row in my_csv:
            if int(row["N_orderUhl"]) >= 43160:
                # first get the predator
                my_pred, created = models.Predator.objects.get_or_create(
                    old_seq_num=row["SeqNoUhl"].strip(),
                    species_id=row["Predator"].strip(),
                )

                # if the predator is being created, populate it with stuff
                # if created or not my_pred.processing_date:
                my_pred.cruise_id = nz(row["cruise_id"].strip(), None)
                my_pred.processing_date = timezone.datetime(int(row["year_pro"]), int(row["month_pro"]), int(row["day_pro"]), tzinfo=timezone.now().tzinfo)
                my_pred.set = nz(row["Set"].strip(), None)
                my_pred.fish_number = nz(row["FishNo"].strip(), None)
                my_pred.somatic_length_cm = nz(row["PredLen"].strip(), None)
                my_pred.stomach_wt_g = nz(row["StomWt"].strip(), None)
                my_pred.comments = nz(row["survey_comment"].strip(), None)
                my_pred.stratum = nz(row["Strat"].strip(), None)
                my_pred.date_last_modified = timezone.now()
                if int(row["Prey"]) != 9900:
                    my_pred.comments = "empty stomach" if not my_pred.comments else "{}; empty stomach".format(my_pred.comments)

                try:
                    my_pred.save()
                except Exception as e:
                    print("cannot save predator.")
                    print(e)
                    print(row["N_orderUhl"])
                    break

                # add in the sampler, if exists
                if nz(row["Sampler"].strip(), None):
                    my_pred.samplers.add(
                        models.Sampler.objects.get(first_name=nz(row["Sampler"].strip(), None))
                    )

                # next get the prey item, if not empty
                if int(row["Prey"]) != 9900:
                    try:
                        my_prey, created = models.Prey.objects.get_or_create(
                            old_id=row["N_orderUhl"].strip(),
                            species_id=row["Prey"].strip(),
                            predator=my_pred,
                        )
                    except Exception as e:
                        print("cannot create prey")
                        print(e)
                        print(row["N_orderUhl"])
                        break
                    else:

                        my_prey.digestion_level_id = nz(row["PreyDigestionState"].strip(), None)
                        my_prey.somatic_length_mm = nz(row["PreyWt"].strip(), None)
                        my_prey.somatic_wt_g = nz(row["PreyLen"].strip(), None)
                        my_prey.censored_length = nz(row["CensoredLen"].strip(), None)
                        my_prey.somatic_wt_g = nz(row["PreyStomWt"].strip(), None)
                        my_prey.comments = nz(row["Comments"].strip(), None)

                        try:
                            my_prey.save()
                        except Exception as e:
                            print("cannot save prey")
                            print(e)
                            print(row["N_orderUhl"])
                            break
