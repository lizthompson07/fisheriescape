# from accounts import models as account_models
from gettext import gettext as _
from django import forms
import django_filters
from django.contrib.auth.models import User

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
chosen_js = {"class": "chosen-select-contains"}


class TripFilter(django_filters.FilterSet):
    class Meta:
        model = models.Trip
        fields = {
            'fiscal_year': ['exact'],
            'trip_title': ['icontains'],
            'section': ['exact'],
            'status': ['exact'],
            'user': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_choices = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in User.objects.all().order_by("last_name", "first_name")
                        if u.user_trips.count() > 0]
        self.filters['user'] = django_filters.ChoiceFilter(field_name='user', lookup_expr='exact', choices=user_choices,
                                                           widget=forms.Select(attrs=chosen_js))


class ConferenceFilter(django_filters.FilterSet):
    class Meta:
        model = models.Conference
        fields = {
            'name': ['icontains'],
            'number': ['icontains'],
        }


class TripApprovalFilter(django_filters.FilterSet):
    class Meta:
        model = models.Trip
        fields = {
            # 'waiting_on': ['exact'],
        }
