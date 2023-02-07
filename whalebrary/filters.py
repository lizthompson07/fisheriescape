import django_filters
from django import forms
from django.db.models import F, DateTimeField, ExpressionWrapper
from django.utils import timezone
from datetime import datetime

from . import models
from django.utils.translation import gettext as _

from .models import Maintenance

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
            'category': ['exact'],
            'owner': ['exact'],
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


class LendingFilter(django_filters.FilterSet):
    class Meta:
        model = models.Transaction
        fields = {
            'comments': ['icontains'],
            'created_by': ['exact'],

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["item"] = django_filters.CharFilter(field_name='search_term',
                                                         label="Items (any part of name...)",
                                                         lookup_expr='icontains',
                                                         widget=forms.TextInput())


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


class MaintenanceFilter(django_filters.FilterSet):

    search_term = django_filters.CharFilter(field_name='search_term', label="Items (any part of name, comments...)",
                                            lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Maintenance
        fields = {
            'assigned_to': ['exact'],
        }

    # This has to be DateTimeFilter to work and not just DateFilter
    maint_due = django_filters.DateTimeFilter(method='days_until_maint', widget=forms.DateInput(attrs=attr_fp_date), label=("Maintenance Due Before"))

    def days_until_maint(self, queryset, name, value):
        return Maintenance.objects.annotate(
            maint=ExpressionWrapper((F('last_maint_date') + F('schedule')), output_field=DateTimeField())
        ).filter(maint__lte=value)


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
