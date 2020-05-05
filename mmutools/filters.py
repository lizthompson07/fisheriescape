import django_filters
from django import forms
from . import models


class ItemFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class SpecificItemFilter(django_filters.FilterSet):
    class Meta:
        model = models.Item
        fields = {
            'item_name': ['icontains'],
            'size': ['icontains'],

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["item_name__icontains"] = django_filters.CharFilter(field_name='search_term',
                                                                         label="Items (any part of name...)",
                                                                         lookup_expr='icontains',
                                                                         widget=forms.TextInput())


class QuantityFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())

class LocationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())

class PersonnelFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class SupplierFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class LendingFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class IncidentFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())
