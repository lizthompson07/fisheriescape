import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _, gettext

from . import models


# class SampleFilter(django_filters.FilterSet):
#     SeasonExact = django_filters.NumberFilter(field_name='year', label="From year", lookup_expr='exact')
#     MonthExact = django_filters.NumberFilter(field_name='month', label="From month", lookup_expr='exact')
#
#     class Meta:
#         model = models.Sample
#         fields = {
#             'id': ['exact'],
#             'station__site': ['exact'],
#             'station': ['exact'],
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.filters.get("station__site").label = "Site"

class RegionFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search term"), lookup_expr='icontains',
                                            widget=forms.TextInput())


class SampleFilter(django_filters.FilterSet):
    SampleDate = django_filters.NumberFilter(field_name='datetime', label="Year", lookup_expr='startswith', widget=forms.NumberInput())

    class Meta:
        model = models.Sample
        fields = {
            'site__region': ['exact'],
            'site': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters.get("site__region").label = gettext("Region")
