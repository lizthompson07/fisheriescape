import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext, gettext_lazy

from shared_models.models import Region, Section
from . import models

chosen_js = {"class": "chosen-select-contains"}


class VehicleFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="search", lookup_expr='icontains', label=gettext_lazy("Search (model, make, reference number)"))

    class Meta:
        model = models.Vehicle
        fields = {
            'id': ['exact'],
            'location__region': ['exact'],
            'location': ['exact'],
            'model': ['icontains'],
            'make': ['icontains'],
            'vehicle_type': ['exact'],
            'max_passengers': ["gte"],
            'is_active': ["exact"],
            'reference_number': ["contains"],
            'custodian': ["exact"],
            'section': ["exact"],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['max_passengers__gte'].label = gettext("Passenger capacity")
        self.filters['location__region'].label = gettext("Region")
        self.filters['reference_number__contains'].label = gettext("Reference number")
        self.filters['location__region'].queryset = Region.objects.filter(vehicle_locations__isnull=False).distinct()
        self.filters['custodian'].queryset = User.objects.filter(vehicles__isnull=False).distinct().order_by("first_name", "last_name")
        self.filters['custodian'].field.widget.attrs = chosen_js

        section_choices = [(s.id, s.full_name) for s in
                           Section.objects.filter(vehicles__isnull=False).distinct().order_by("division__branch__region", "division__branch",
                                                                        "division", "name")]
        self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=gettext("Section"),
                                                              lookup_expr='exact', choices=section_choices, widget=forms.Select(attrs=chosen_js))


class ReservationFilter(django_filters.FilterSet):
    # start = django_filters.DateTimeFilter(field_name="start_date", lookup_expr='gte')
    # end = django_filters.DateTimeFilter(field_name="end_date", lookup_expr='lte')
    location = django_filters.ModelChoiceFilter(field_name="vehicle__location", lookup_expr='exact', queryset=models.Location.objects.all())
    vehicle_type = django_filters.ModelChoiceFilter(field_name="vehicle__vehicle_type", lookup_expr='exact', queryset=models.VehicleType.objects.all())
    max_passengers__gte = django_filters.NumberFilter(field_name="vehicle__max_passengers__gte", lookup_expr='gte')

    class Meta:
        model = models.Reservation
        fields = {
            'vehicle': ['exact'],

        }


class SimpleReservationFilter(django_filters.FilterSet):
    custodian = django_filters.ModelChoiceFilter(field_name="vehicle__custodian", lookup_expr='exact', queryset=Region.objects.all(),
                                                 label=gettext_lazy("Custodian"))
    region = django_filters.ModelChoiceFilter(field_name="location__region", lookup_expr='exact', queryset=Region.objects.all(), label=gettext_lazy("Region"))

    class Meta:
        model = models.Reservation
        fields = {
            'status': ['exact'],
            'vehicle': ['exact'],
            'primary_driver': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['region'].queryset = Region.objects.filter(vehicle_locations__isnull=False).distinct()
        self.filters['custodian'].queryset = User.objects.filter(vehicles__isnull=False).distinct().order_by("first_name", "last_name")
        self.filters['primary_driver'].queryset = User.objects.filter(vehicle_reservations__isnull=False).distinct().order_by("first_name", "last_name")
        self.filters['custodian'].field.widget.attrs = chosen_js
        self.filters['primary_driver'].field.widget.attrs = chosen_js
        self.filters['vehicle'].field.widget.attrs = chosen_js

        # vehicle_choices = [(v.id, str(v)) for v in models.Vehicle.objects.all()]
        # self.filters['id'].field.choices = vehicle_choices


class FAQFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="search", lookup_expr='icontains', label=gettext_lazy("Search"))
