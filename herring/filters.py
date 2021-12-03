import django_filters
from django import forms

from . import models


class SampleFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.filters['sampling_protocol'].label = 'Protocol'
        self.filters['id'].label = 'Sample #'
        # self.filters['SampleDate'].label = 'Sample collection date'
        self.filters['season'].label = 'Year'
        self.filters['sampler_ref_number'].label = "Sampler ref. no."
        self.filters['experimental_net_used'].label = "Experimental?"
        print(self.filters)
        self.filters['survey_id__icontains'].label = "Survey identifier (any part)"

    class Meta:
        model = models.Sample
        fields = {
            'id': ['exact'],
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
