import django_filters

from django_filters.filters import OrderingFilter
from django import forms
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

from masterlist import models as ml_models
from maret import models

ind_organizations = ml_models.Organization.objects.filter(grouping__is_indigenous=True)
chosen_js = {"class": "chosen-select-contains"}


class InteractionFilter(django_filters.FilterSet):
    class Meta:
        model = models.Interaction
        fields = ["interaction_type", "dfo_liaison", "main_topic", "external_organization", "external_contact"]


class CommitteeFilter(django_filters.FilterSet):
    class Meta:
        model = models.Committee
        fields = ["name", "branch", "division", "external_organization", "external_contact"]


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Search organizations (name, province, etc...)"),
                                            lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = ml_models.Organization
        fields = {
            'regions': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['regions'].field.widget.attrs = chosen_js


class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = ml_models.Person
        fields = {
            'last_name': ['exact'],
            'memberships__role': ['icontains'],
            'organizations': ['exact'],
            'organizations__regions': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['memberships__role__icontains'].label = mark_safe(_("Organizational role <br>(any part of name)"))
        self.filters['organizations'] = django_filters.ModelChoiceFilter(field_name="organizations",
                                                                         queryset=ind_organizations,
                                                                         widget=forms.Select(attrs=chosen_js))
        self.filters["last_name"] = django_filters.CharFilter(field_name='search_term', label=_("Any part of name, or title"),
                                                              lookup_expr='icontains', widget=forms.TextInput())
        self.filters['organizations__regions'].label = _("DFO Region")
        self.filters['organizations__regions'].field.widget.attrs = chosen_js
