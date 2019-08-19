import csv
import datetime
import os

from lib.templatetags.custom_filters import nz
from . import models
from shared_models import models as shared_models


def import_nb_county_polygons():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "nb_county_polygons.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        # count = 0
        for row in my_csv:
            # get or create the name of the county
            my_region, created = models.Region.objects.get_or_create(
                name=row["ENG_NAME"],
                province_id=1
            )
            # update the french name
            my_region.nom = row["FRE_NAME"]
            my_region.save()

            # create a new polygon
            my_poly, created = models.RegionPolygon.objects.get_or_create(
                region=my_region,
                old_id=row["ID"],
            )


def import_nb_county_points():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "nb_county_points.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        # count = 0
        for row in my_csv:
            # get or create the name of the county
            my_region = models.Region.objects.get(
                name=row["ENG_NAME"],
                province_id=1
            )

            # create a new polygon
            my_poly = models.RegionPolygon.objects.get(
                region=my_region,
                old_id=row["ID"],
            )

            # clear any existing point associated with this polygon
            # my_poly.points.all().delete()

            my_poly.points.create(
                latitude=float(row["y"]),
                longitude=float(row["x"]),
            )




def import_ns_county_polygons():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "ns_county_polygons.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        # count = 0
        for row in my_csv:
            # get or create the name of the county
            my_region, created = models.Region.objects.get_or_create(
                name=row["county"],
                province_id=3
            )
            # update the french name
            my_region.nom = row["county"]
            my_region.save()

            # create a new polygon
            my_poly, created = models.RegionPolygon.objects.get_or_create(
                region=my_region,
                old_id=row["ID"],
            )


def import_ns_county_points():
    # open the csv we want to read
    rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    with open(os.path.join(rootdir, "ns_county_points.csv"), 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        # count = 0
        for row in my_csv:
            # get or create the name of the county
            my_region = models.Region.objects.get(
                name=row["county"],
                province_id=3
            )

            # create a new polygon
            my_poly = models.RegionPolygon.objects.get(
                region=my_region,
                old_id=row["ID"],
            )

            my_poly.points.create(
                latitude=float(row["y"]),
                longitude=float(row["x"]),
            )
