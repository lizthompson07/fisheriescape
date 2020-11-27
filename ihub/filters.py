from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from . import models
import django_filters
from masterlist import models as ml_models

ind_organizations = ml_models.Organization.objects.filter(grouping__is_indigenous=True)
chosen_js = {"class": "chosen-select-contains"}


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search organizations (name, province, etc...)"),
                                            lookup_expr='icontains', widget=forms.TextInput())


class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = ml_models.Person
        fields = {
            'last_name': ['exact'],
            'organizations': ['exact'],
            'memberships__role': ['icontains'],
        }
        labels = {
            'memberships__role': "Membership roles",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['organizations'] = django_filters.ModelChoiceFilter(field_name="organizations",
                                                                         queryset=ind_organizations,
                                                                         widget=forms.Select(attrs=chosen_js))
        self.filters["last_name"] = django_filters.CharFilter(field_name='search_term', label=_("Any part of name, or title"),
                                                              lookup_expr='icontains', widget=forms.TextInput())


class EntryFilter(django_filters.FilterSet):
    class Meta:
        model = models.Entry
        fields = {
            'title': ['icontains'],
            'status': ['exact'],
            'entry_type': ['exact'],
            'organizations': ['exact'],
            'sectors': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['organizations'].queryset = ind_organizations


class UserFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Name contains"), lookup_expr='icontains',
                                            widget=forms.TextInput())
