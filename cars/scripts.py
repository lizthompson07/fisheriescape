import csv
import datetime
import os

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware, now, get_current_timezone

from shared_models.utils import dotdict
from . import models

def copy_over_rsvp():
    my_target_read_file = os.path.join(settings.BASE_DIR, 'cars', 'misc', 'rsvps.csv')
    with open(os.path.join(my_target_read_file), 'r', encoding='cp1252') as read_file:
        reader = csv.DictReader(read_file)
        i = 1
        for row in reader:
            rowdict = dotdict(row)

            # get car
            ref = rowdict.id
            ref = f"{ref[:2]}-{ref[2:]}"
            v = get_object_or_404(models.Vehicle, reference_number=ref)

            # get start + end
            start = make_aware(datetime.datetime.strptime(rowdict.start, "%Y-%m-%d"), get_current_timezone())
            end = make_aware(datetime.datetime.strptime(rowdict.end, "%Y-%m-%d"), get_current_timezone())

            # get user
            user_str = rowdict.primary
            first = user_str.split(" ")[0]
            last = user_str.split(" ")[1]

            qs = User.objects.filter(first_name__istartswith=first, last_name__istartswith=last)
            if qs.count() != 1:
                # try with email
                qs = User.objects.filter(email__iexact=f"{first}.{last}@dfo-mpo.gc.ca")
                if qs.count() != 1:
                    print(first, last, qs.count())
                    user = None
                else:
                    user = qs.first()
            else:
                user = qs.first()

            if user:
                models.Reservation.objects.get_or_create(
                    status=10,
                    primary_driver=user,
                    vehicle=v,
                    start_date=start,
                    end_date=end,
                    destination=rowdict.destination,
                    comments=f"Other drivers / passengers: {rowdict.other}",
                )

            i += 1
