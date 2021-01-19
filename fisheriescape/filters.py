import django_filters
from django import forms
from . import models
from django.utils.translation import gettext as _

attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}


class SpeciesFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='start_date', lookup_expr='lt',
                                           label='Start date is before (mm/dd/yyyy):',
                                           widget=forms.DateInput(attrs=attr_fp_date))

    class Meta:
        model = models.Species
        fields = {
            'fishery_area': ['exact'],
            'fishery_status': ['exact'],
            'gear_type': ['exact'],

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["english_name__icontains"] = django_filters.CharFilter(field_name='search_term',
                                                                            label="Species (any language)",
                                                                            lookup_expr='icontains',
                                                                            widget=forms.TextInput())


class FisheryAreaFilter(django_filters.FilterSet):
    class Meta:
        model = models.FisheryArea
        fields = {
            'name': ['icontains'],
            'region': ['exact'],

        }
