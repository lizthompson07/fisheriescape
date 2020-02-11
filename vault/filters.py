import django_filters
from . import models
from django import forms

#
class SpeciesFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())

class ObservationPlatformFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())

class ItemsFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())
# class PredatorFilter(django_filters.FilterSet):
#     search_term = django_filters.CharFilter(field_name='search_term', label="Species (any part of name...)",
#                                             lookup_expr='icontains', widget=forms.TextInput())
#     id = django_filters.CharFilter(field_name='processing_date', label="Season",
#                                             lookup_expr='icontains', widget=forms.NumberInput())
#     class Meta:
#         model = models.Predator
#         fields = {
#             # placeholder for season filter, defined above
#             'id': ['exact'],
#             'cruise': ['exact'],
#             'stomach_id': ['exact'],
#             'samplers': ['exact'],
#         }
#
#
