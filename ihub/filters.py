# from accounts import models as account_models
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone

from . import models
import django_filters

class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search organizations (name, abbreviation, etc...)",
                                            lookup_expr='icontains', widget=forms.TextInput())

class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search",
                                            lookup_expr='icontains', widget=forms.TextInput())


class EntryFilter(django_filters.FilterSet):
    # FY_CHOICES = [("{}-{}".format(y, y + 1), "{}-{}".format(y, y + 1)) for y in
    #               range(timezone.now().year - 2, timezone.now().year + 1)]
    # # SECTION_CHOICES = [(None, "----"),]
    # DIVISION_CHOICES = [(d.id, str(d)) for d in models.Division.objects.all()]
    SECTION_CHOICES = [(s.id, str(s)) for s in models.Sector.objects.all()]

    # fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=FY_CHOICES)
    # project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
    # division = django_filters.ChoiceFilter(field_name='division', lookup_expr='exact', choices=DIVISION_CHOICES)
    section = django_filters.MultipleChoiceFilter(field_name='sector', lookup_expr='exact', choices=SECTION_CHOICES, label="Sector (shift+click)")

    class Meta:
        model = models.Entry
        fields = {
            'title': ['icontains'],
            'status': ['exact'],
            'entry_type': ['exact'],
            'organizations': ['exact'],
            # 'created_by': ['exact'],
        }

