import django_filters
from django.forms import HiddenInput
from django.utils.translation import gettext

from . import models

chosen_js = {"class": "chosen-select-contains"}


class VehicleFilter(django_filters.FilterSet):
    # id = django_filters.MultipleChoiceFilter("id")
    class Meta:
        model = models.Vehicle
        fields = {
            'id': ['exact'],
            'location': ['exact'],
            'vehicle_type': ['exact'],
            'max_passengers': ["gte"],
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['max_passengers__gte'].label = gettext("Passenger capacity")

        # vehicle_choices = [(v.id, str(v)) for v in models.Vehicle.objects.all()]
        # self.filters['id'].field.choices = vehicle_choices
        # self.filters['id'].field.widget = HiddenInput()


class ReservationFilter(django_filters.FilterSet):
    class Meta:
        model = models.Reservation
        fields = {
            'vehicle': ['exact'],

        }
