import django_filters
from django import forms
from django.utils import timezone

from . import models


class TicketFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Key term (title, description, notes, Id):",
                                            lookup_expr='icontains', widget=forms.TextInput())
    class Meta:
        model = models.Ticket
        fields = {
            'fiscal_year': ['exact'],
            'status': ['exact'],
            'section': ['exact'],
        }


class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = models.Person
        fields = {
            'first_name': ['icontains'],
            'last_name': ['icontains'],

        }


class TagFilter(django_filters.FilterSet):
    class Meta:
        model = models.Tag
        fields = {
            'tag': ['icontains'],
        }


class FiscalFilter(django_filters.FilterSet):
    FY_CHOICES = [("{}-{}".format(y, y + 1), "{}-{}".format(y, y + 1)) for y in range(timezone.now().year - 2, timezone.now().year + 1)]
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=FY_CHOICES)
