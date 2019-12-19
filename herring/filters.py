import django_filters
from . import models
from django import forms


class SampleFilter(django_filters.FilterSet):
    # SeasonSince = django_filters.NumberFilter(field_name='season', label="Since year", lookup_expr='gte', widget= forms.NumberInput())
    # SeasonExact = django_filters.NumberFilter(field_name='season', label="From year", lookup_expr='exact', widget= forms.NumberInput())
    # SampleDate = django_filters.DateFilter(field_name='sample_date', label="Sample date", lookup_expr='startswith',
    #                                        widget=forms.DateInput(attrs={'type': 'date', }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.filters['sampling_protocol'].label = 'Protocol'
        self.filters['id'].label = 'Sample #'
        # self.filters['SampleDate'].label = 'Sample collection date'
        self.filters['season'].label = 'Year'
        self.filters['sampler_ref_number'].label = "Sampler ref. no."
        self.filters['experimental_net_used'].label = "Experimental?"

    class Meta:
        model = models.Sample
        fields = {
            'id': ['exact'],
            'season':['exact'],
            'sampler_ref_number': ['exact'],
            'experimental_net_used': ['exact'],
            'type': ['exact'],
            'sampler': ['exact'],
            # 'sample_date': ['exact'],
        }


class SamplerFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search",
                                            lookup_expr='icontains', widget=forms.TextInput())
