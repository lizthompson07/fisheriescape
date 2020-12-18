import django_filters
from django.utils.translation import gettext_lazy as _

from . import models
from django import forms


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
