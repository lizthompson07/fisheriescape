import django_filters
from . import models
from django import forms

class SampleFilter(django_filters.FilterSet):
    SeasonExact = django_filters.NumberFilter(field_name='season', label="Year", lookup_expr='exact', widget= forms.NumberInput(attrs={'style':"width: 4em"}))

    class Meta:
        model = models.Sample
        fields = {
            'station':['exact'],
            # 'sampler':['exact'],
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.filters['season'].extra.update(
                {'empty_label': 'All Manufacturers'})


class StationFilter(django_filters.FilterSet):
    class Meta:
        model = models.Station
        fields = {
            'station_name':['icontains'],
            'province':['exact'],
        }


class ReportFilter(django_filters.FilterSet):
    class Meta:
        model = models.IncidentalReport
        fields = {
            'season':['exact'],
            'report_type':['exact'],
        }


class SpeciesFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Species (any part of name...)", lookup_expr='icontains', widget= forms.TextInput())



class SpeciesFilterFull(django_filters.FilterSet):
    class Meta:
        model = models.Species
        fields = {
            'common_name': ['icontains'],
            'scientific_name': ['icontains'],
            'tsn':['exact'],
            'aphia_id':['exact'],
            'biofouling':['exact'],
            'invasive':['exact'],
            'color_morph':['exact'],
        }
        labels = {
            'tsn':"TSN",
            
        }
