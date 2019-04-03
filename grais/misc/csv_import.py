import os
import csv
import datetime
from .. import models

rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"

# open the csv we want to read

def seed_db():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump\\greencrab"
    with open(os.path.join(rootdir, "green_crab_2016.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        i = 0
        for row in my_csv:
            if i < 10:
                # step 1: create a sample

                my_site = models.Site.objects.get(code=row["site_code"])
                traps_set = datetime.datetime.strptime(row["td1"], "%d/%m/%Y %H:%M")
                my_sample, created = models.GCSample.objects.get_or_create(site=my_site, traps_set=traps_set)
                print(my_sample)
                print(created)
                my_sample.save()
                i += 1

            #
        #
        #
        #
        #
        # site = models.ForeignKey(Site, related_name='samples', on_delete=models.DO_NOTHING)
        # traps_set = models.DateTimeField()
        # traps_fished = models.DateTimeField(blank=True, null=True)
        # samplers = models.ManyToManyField(Sampler)
        # bottom_type = models.CharField(max_length=100, blank=True, null=True)
        # percent_vegetation_cover = models.IntegerField(blank=True, null=True, verbose_name="vegetation cover (%)",
        #                                                validators=[MinValueValidator(0), MaxValueValidator(100)])
        # season = models.IntegerField(null=True, blank=True)
        # last_modified = models.DateTimeField(blank=True, null=True)
        # last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)
        # notes = models.TextField(blank=True, null=True)
        # temp_notes = models.CharField(max_length=1000, blank=True, null=True)
        #

        # my_obs, created = models.SpeciesObservations.objects.get_or_create( sample_id=int(row["sample_id"]), species_id= int(row["species_id"]) )
        # if created:
        #     print(row)
        #     stage = row["stage"]
        #     value = float(row["value"])
        #     if stage:
        #         if stage == "A":
        #             my_obs.adults = value
        #         elif stage == "YOY":
        #             my_obs.yoy = value
        #     else:
        #         my_obs.unknown = value
        #     my_obs.save()
