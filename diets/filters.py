import django_filters
from . import models
from django import forms


class SpeciesFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Species (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class PredatorFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Species (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Predator
        fields = {
            'cruise': ['exact'],
            'stomach_id': ['exact'],
            'samplers': ['exact'],
        }
