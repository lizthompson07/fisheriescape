from django import forms
from django.utils.translation import gettext as _
from . import models
import django_filters
from masterlist import models as ml_models

ind_organizations = ml_models.Organization.objects.filter(grouping__is_indigenous=True)



class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search organizations (name, abbreviation, etc...)"),
                                            lookup_expr='icontains', widget=forms.TextInput())

class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search"),
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
        print(self.filters['organizations'])
        self.filters['organizations'].queryset = ind_organizations
