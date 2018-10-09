import django_filters
from . import models
from django import forms

class SampleFilter(django_filters.FilterSet):
    SeasonSince = django_filters.NumberFilter(field_name='season', label="Since year", lookup_expr='gte', widget= forms.NumberInput())
    SeasonExact = django_filters.NumberFilter(field_name='season', label="From year", lookup_expr='exact', widget= forms.NumberInput())
    SamplerRefNumber = django_filters.NumberFilter(field_name='sampler_ref_number', label="Sampler's reference no.", lookup_expr='exact', widget= forms.NumberInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['sampling_protocol'].label = 'Protocol'


    class Meta:
        model = models.Sample
        fields = {
            # 'sampler_ref_number':['exact'],
            'sampling_protocol':['exact'],
        }
