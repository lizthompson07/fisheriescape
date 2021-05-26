import django_filters
from django import forms
from . import models
from django.utils.translation import gettext as _

attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}


class ItemFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name or description)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class SpecificItemFilter(django_filters.FilterSet):
    class Meta:
        model = models.Item
        fields = {
            'item_name': ['icontains'],
            'size': ['exact'],
            'suppliers': ['exact'],

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["item_name__icontains"] = django_filters.CharFilter(field_name='search_term',
                                                                         label="Items (any part of name or description)",
                                                                         lookup_expr='icontains',
                                                                         widget=forms.TextInput())


class TransactionFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of any field...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class BulkTransactionFilter(django_filters.FilterSet):
    class Meta:
        model = models.Transaction
        fields = {
            'category': ['exact'],
            'comments': ['icontains'],

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["item"] = django_filters.CharFilter(field_name='search_term',
                                                         label="Items (any part of name...)",
                                                         lookup_expr='icontains',
                                                         widget=forms.TextInput())


class OrderFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class LocationFilter(django_filters.FilterSet):
    class Meta:
        model = models.Location
        fields = {
            'container': ['exact'],

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["location__icontains"] = django_filters.CharFilter(field_name='search_term',
                                                                        label="Locations (any part of location or address)",
                                                                        lookup_expr='icontains',
                                                                        widget=forms.TextInput())


class PersonnelFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class SupplierFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class FileFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Files (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


# class IncidentFilter(django_filters.FilterSet):
#     search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
#                                             lookup_expr='icontains', widget=forms.TextInput())

class IncidentFilter(django_filters.FilterSet):

    date_between = django_filters.DateFromToRangeFilter(field_name='first_report',
                                                        label='Incident (Between these dates)',
                                                        widget=django_filters.widgets.RangeWidget(attrs=attr_fp_date))

    class Meta:
        model = models.Incident
        fields = {
            'region': ['exact'],
            'species': ['exact'],
            'incident_type': ['exact'],

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["name"] = django_filters.CharFilter(field_name='search_term',
                                                         label="Incident (any part of name...)",
                                                         lookup_expr='icontains',
                                                         widget=forms.TextInput())


class ResightFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class ImageFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Image (any part of name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class UserFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Name contains"), lookup_expr='icontains',
                                            widget=forms.TextInput())
