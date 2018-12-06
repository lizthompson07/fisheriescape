from .import models

import os
import csv

def resave_all_samples(samples = models.Sample.objects.all()):
    for s in samples:
        s.save()

def resave_all_obs():
    species_obs = models.SpeciesObservation.objects.filter(species__sav=True)
    for obj in species_obs:
        obj.save()

def seed_db():

    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "row_by_col.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        for row in my_csv:
            my_obs, created = models.SpeciesObservations.objects.get_or_create( sample_id=int(row["sample_id"]), species_id= int(row["species_id"]) )
            if created:
                print(row)
                stage = row["stage"]
                value = float(row["value"])
                if stage:
                    if stage == "A":
                        my_obs.adults = value
                    elif stage == "YOY":
                        my_obs.yoy = value
                else:
                    my_obs.unknown = value
                my_obs.save()

