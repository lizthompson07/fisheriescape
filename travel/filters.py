# from accounts import models as account_models
from gettext import gettext as _
from django import forms
import django_filters
from . import models

# YES_NO_CHOICES = (
#     (True, "Yes"),
#     (False, "No"),
# )
#
# class OrganizationFilter(django_filters.FilterSet):
#     search_term = django_filters.CharFilter(field_name='search_term', label="Search organizations (name, abbreviation, etc...)",
#                                             lookup_expr='icontains', widget=forms.TextInput())
#     indigenous = django_filters.ChoiceFilter(field_name='grouping__is_indigenous', choices=YES_NO_CHOICES, label=_("Indigenous?"),)
#
class EventFilter(django_filters.FilterSet):
    class Meta:
        model = models.Event
        fields = {
            'fiscal_year':['exact'],
            'trip_title':['icontains'],
            'section':['exact'],
        }


