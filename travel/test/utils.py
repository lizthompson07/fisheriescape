from datetime import timedelta

from django.db import IntegrityError
from django.utils import timezone
from faker import Faker

from shared_models.models import Region, Section
from travel.models import Trip, DefaultReviewer
from travel.test import FactoryFloor

faker = Faker()


def create_trip_for_adm_review(trip_id=None):
    gulf = Region.objects.get(name__iexact="gulf")
    adm = DefaultReviewer.objects.filter(special_role=5).first().user
    rdg = Region.objects.filter(travel_default_reviewers__isnull=False).distinct().first().head

    if not trip_id:
        trip = FactoryFloor.TripFactory(is_adm_approval_required=True, lead=gulf)
    else:
        trip = Trip.objects.get(id=trip_id)

    # some modifications
    if trip.start_date < timezone.now():
        trip.start_date = trip.start_date + timedelta(days=100)
        trip.end_date = trip.start_date + timedelta(days=100)
    trip.status = 31
    trip.review_start_date = timezone.now()
    trip.save()
    FactoryFloor.TripReviewerFactory(user=adm, status=25, role=5, trip=trip)

    trip.requests.all().delete()

    # create three different trip requests
    section = Section.objects.filter(division__branch__sector__region=gulf).first()
    late_justification = "blah blah"
    request1 = FactoryFloor.TripRequestFactory(trip=trip, section=section, status=14, late_justification=late_justification, submitted=timezone.now())
    request2 = FactoryFloor.TripRequestFactory(trip=trip, section=section, status=14, late_justification=late_justification, submitted=timezone.now())
    request3 = FactoryFloor.TripRequestFactory(trip=trip, section=section, status=14, late_justification=late_justification, submitted=timezone.now())

    # travellers
    requests = [request1, request2, request3]

    for request in requests:
        # add reviewers
        FactoryFloor.ReviewerFactory(request=request, user=adm, status=1, role=5, order=1)
        FactoryFloor.ReviewerFactory(request=request, user=rdg, status=20, role=7, order=2)

        # add travellers
        for i in range(0, faker.pyint(2, 10)):
            t = FactoryFloor.TravellerFactory(request=request, start_date=trip.start_date, end_date=trip.end_date)
            for i in range(0, faker.pyint(2, 10)):
                try:
                    FactoryFloor.TravellerCostFactory(traveller=t)
                except IntegrityError:
                    pass


def create_trip_for_rds_review(trip_id=None):
    gulf = Region.objects.get(name__iexact="gulf")

    if not trip_id:
        trip = FactoryFloor.TripFactory(is_adm_approval_required=True, lead=gulf)
    else:
        trip = Trip.objects.get(id=trip_id)

    # some modifications
    if trip.start_date < timezone.now():
        trip.start_date = trip.start_date + timedelta(days=100)
        trip.end_date = trip.start_date + timedelta(days=100)
    trip.status = 41
    trip.save()
    trip.requests.all().delete()
    print(trip.id, trip)
    # create three different trip requests
    section = Section.objects.filter(division__branch__sector__region=gulf).first()
    late_justification = "blah blah"
    request1 = FactoryFloor.TripRequestFactory(trip=trip, section=section, status=12, late_justification=late_justification, submitted=timezone.now())
    request2 = FactoryFloor.TripRequestFactory(trip=trip, section=section, status=12, late_justification=late_justification, submitted=timezone.now())
    request3 = FactoryFloor.TripRequestFactory(trip=trip, section=section, status=12, late_justification=late_justification, submitted=timezone.now())

    # travellers
    requests = [request1, request2, request3]

    for request in requests:
        # add reviewers
        FactoryFloor.ReviewerFactory(request=request, user_id=50, status=1, role=2, order=1)

        # add travellers
        for i in range(0, faker.pyint(2, 10)):
            t = FactoryFloor.TravellerFactory(request=request, start_date=trip.start_date, end_date=trip.end_date)
            for i in range(0, faker.pyint(2, 10)):
                try:
                    FactoryFloor.TravellerCostFactory(traveller=t)
                except IntegrityError:
                    pass
