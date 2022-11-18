import django_filters
from django import forms
from django.utils.translation import gettext_lazy

from . import models


class SpeciesFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=gettext_lazy("Search term"), lookup_expr='icontains',
                                            widget=forms.TextInput())


class PortFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=gettext_lazy("Search term"), lookup_expr='icontains',
                                            widget=forms.TextInput())


class SampleFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['id'].label = 'Sample ID'
        self.filters['season'].label = 'Year'
        self.filters['experimental_net_used'].label = "Experimental?"
        self.filters['survey_id__icontains'].label = "Survey identifier (any part)"

    class Meta:
        model = models.Sample
        fields = {
            'id': ['exact'],
            'species': ['exact'],
            'season': ['exact'],
            'season_type': ['exact'],
            'sampler_ref_number': ['exact'],
            'experimental_net_used': ['exact'],
            'type': ['exact'],
            'sampler': ['exact'],
            'survey_id': ['icontains'],
        }


class SamplerFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search",
                                            lookup_expr='icontains', widget=forms.TextInput())
