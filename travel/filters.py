# from accounts import models as account_models
# from  import gettext as _
import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from shared_models import models as shared_models
from . import models
from .utils import get_region_choices, get_division_choices, get_section_choices

chosen_js = {"class": "chosen-select-contains"}


class TripRequestFilter(django_filters.FilterSet):
    class Meta:
        model = models.TripRequest
        fields = {
            'fiscal_year': ['exact'],
            'trip': ['exact'],
            'status': ['exact'],
            # 'user': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user_choices = [(u.id, f"{u.last_name}, {u.first_name}") for u in
                        User.objects.filter(user_trip_requests__isnull=False).distinct().order_by("last_name", "first_name")]

        self.filters['user'] = django_filters.ChoiceFilter(field_name='user', lookup_expr='exact', choices=user_choices,
                                                           widget=forms.Select(attrs=chosen_js), label=_('User'))

        trip_choices = [(trip.id, f"{trip}") for trip in models.Conference.objects.filter(trip_requests__isnull=False).distinct().order_by(_("name")) ]


        self.filters['trip'] = django_filters.ChoiceFilter(field_name='trip', lookup_expr='exact', choices=trip_choices,
                                                           widget=forms.Select(attrs=chosen_js), label=_('Trip title'))

        region_choices = get_region_choices()
        division_choices = get_division_choices()
        section_choices = get_section_choices(all=True)
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.filter(trip_requests__isnull=False).distinct()]

        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=fy_choices,
                                                                  label=_("Fiscal year"))
        self.filters['region'] = django_filters.ChoiceFilter(field_name="section__division__branch__region", label=_("Region"),
                                                             lookup_expr='exact', choices=region_choices)
        self.filters['division'] = django_filters.ChoiceFilter(field_name="section__division", label=_("Division"),
                                                               lookup_expr='exact', choices=division_choices)
        self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"),
                                                              lookup_expr='exact', choices=section_choices)

        try:
            # if there is a filter on region, filter the division and section filter accordingly
            if self.data["region"] != "":
                my_region_id = int(self.data["region"])
                division_choices = [my_set for my_set in get_division_choices() if
                                    shared_models.Division.objects.get(pk=my_set[0]).branch.region_id == my_region_id]
                self.filters['division'] = django_filters.ChoiceFilter(field_name="section__division", label=_("Division"),
                                                                       lookup_expr='exact', choices=division_choices)

                section_choices = [my_set for my_set in get_section_choices(all=True) if
                                   shared_models.Section.objects.get(pk=my_set[0]).division.branch.region_id == my_region_id]
                self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"),
                                                                      lookup_expr='exact', choices=section_choices)

            # if there is a filter on division, filter the section filter accordingly
            if self.data["division"] != "":
                my_division_id = int(self.data["division"])

                section_choices = [my_set for my_set in get_section_choices(all=True) if
                                   shared_models.Section.objects.get(pk=my_set[0]).division_id == my_division_id]
                self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"),
                                                                      lookup_expr='exact', choices=section_choices)

        except KeyError:
            pass


class TripFilter(django_filters.FilterSet):
    class Meta:
        model = models.Conference
        fields = {
            'name': ['exact'],
            'fiscal_year': ['exact'],
            'lead': ['exact'],
            'is_adm_approval_required': ['exact'],
            'status': ['exact'],
            'trip_subcategory': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.filter(trips__isnull=False).distinct()]
        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=fy_choices,
                                                                  label=_("Fiscal year"))
        self.filters['name'] = django_filters.CharFilter(field_name='search_term', label=_("Trip Title"), lookup_expr='icontains',
                                                         widget=forms.TextInput())
        self.filters['lead'].label = _("Regional lead")
        self.filters['is_adm_approval_required'].label = _("ADM approval required?")


class TripRequestApprovalFilter(django_filters.FilterSet):
    class Meta:
        model = models.TripRequest
        fields = {
            # 'waiting_on': ['exact'],
        }


class UserFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Name contains"), lookup_expr='icontains',
                                            widget=forms.TextInput())
