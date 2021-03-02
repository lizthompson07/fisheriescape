import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy

from masterlist import models as ml_models
from . import models

ind_organizations = ml_models.Organization.objects.filter(grouping__is_indigenous=True)
chosen_js = {"class": "chosen-select-contains"}


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=gettext_lazy("Search organizations (name, province, etc...)"),
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


class EntryFilter(django_filters.FilterSet):
    class Meta:
        model = models.Entry
        fields = {
            'title': ['icontains'],
            'status': ['exact'],
            'entry_type': ['exact'],
            'organizations': ['exact'],
            'sectors': ['exact'],
            'regions': ['exact'],
            'people__user': ['exact'],
            'created_by': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['organizations'].queryset = ind_organizations
        self.filters['people__user'].queryset = User.objects.filter(ihub_entry_people__isnull=False).order_by("first_name", "last_name").distinct()
        self.filters['created_by'].queryset = User.objects.filter(user_entries__isnull=False).order_by("first_name", "last_name").distinct()
        self.filters['people__user'].label = _("Entry Contact")
        self.filters['title__icontains'].label = _("title contains")

        self.filters['organizations'].field.widget.attrs = chosen_js
        self.filters['sectors'].field.widget.attrs = chosen_js
        self.filters['regions'].field.widget.attrs = chosen_js
        self.filters['people__user'].field.widget.attrs = chosen_js
        self.filters['created_by'].field.widget.attrs = chosen_js



class UserFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Name contains"), lookup_expr='icontains',
                                            widget=forms.TextInput())
