from django.db import IntegrityError

from . import models


def get_reviewers(trip):
    # if in gulf region, add Amelie as a reviewer
    if trip.region_id == 1:
        try:
            models.Reviewer.objects.create(trip=trip, user_id=385, role_id=1, )
        except IntegrityError:
            print("not adding amelie")

    # assuming there is a section, assign section management
    if trip.section:
        # try adding section head, division manager and rds
        try:
            models.Reviewer.objects.create(trip=trip, user=trip.section.head, role_id=2, )
        except (IntegrityError, AttributeError):
            print("not adding section head")
        try:
            models.Reviewer.objects.create(trip=trip, user=trip.section.division.head, role_id=2, )
        except (IntegrityError, AttributeError):
            print("not adding division manager")
        try:
            models.Reviewer.objects.create(trip=trip, user=trip.section.division.branch.head, role_id=2, )
        except (IntegrityError, AttributeError):
            print("not adding RDS")

    # should the ADMs office be invovled?
    if trip.is_international or trip.is_conference:
        # add the ADMs office staff
        try:
            models.Reviewer.objects.create(trip=trip, user_id=749, role_id=3, ) # Kim Cotton
        except IntegrityError:
            print("not adding NCR reviewer")
        try:
            models.Reviewer.objects.create(trip=trip, user_id=736, role_id=4, ) # Andy White
        except IntegrityError:
            print("not adding NCR recommender")
        try:
            models.Reviewer.objects.create(trip=trip, user_id=754, role_id=4, ) # Stephen Birc
        except IntegrityError:
            print("not adding NCR recommender")
        try:
            models.Reviewer.objects.create(trip=trip, user_id=740, role_id=4, )  # Wayne Moore
        except IntegrityError:
            print("not adding NCR recommender")
        try:
            models.Reviewer.objects.create(trip=trip, user_id=626, role_id=5, )  # Arran McPherson
        except IntegrityError:
            print("not adding NCR ADM")

    # finally, we always need to add the RDG
    try:
        models.Reviewer.objects.create(trip=trip, user=trip.section.division.branch.region.head, role_id=6, )
    except (IntegrityError, AttributeError):
        print("not adding RDG")
