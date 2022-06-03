import django_filters

from . import models

chosen_js = {"class": "chosen-select-contains"}


class VehicleFilter(django_filters.FilterSet):
    class Meta:
        model = models.Vehicle
        fields = {
            'region': ['exact'],
            'location': ['exact'],
            'vehicle_type': ['exact'],
            'max_passengers': ['exact'],
        }
