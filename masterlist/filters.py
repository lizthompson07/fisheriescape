# from accounts import models as account_models
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone

from . import models
import django_filters

class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search organizations (name, abbreviation, etc...)",
                                            lookup_expr='icontains', widget=forms.TextInput())
    indigenous = django_filters.ChoiceFilter(field_name='groupins__is_indigenour')

class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search",
                                            lookup_expr='icontains', widget=forms.TextInput())



