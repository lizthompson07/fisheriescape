from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import django_filters
from . import views
from . import models
from . import utils

chosen_js = {"class": "chosen-select-contains"}


class SectionFilter(django_filters.FilterSet):
    section = django_filters.ChoiceFilter(field_name='name')
    division = django_filters.ChoiceFilter(field_name='division')
    branch = django_filters.ChoiceFilter(field_name='division__branch')
    region = django_filters.ChoiceFilter(field_name="division__branch__region")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region_label = _("Region - Sector (NCR)")
        branch_label = _("Branch - Directorate (NCR)")
        division_label = _("Division - Branch (NCR)")
        section_label = _("Section - Team (NCR)")
        region_choices = utils.get_region_choices()
        branch_choices = utils.get_branch_choices()
        division_choices = utils.get_division_choices()

        self.filters['section'] = django_filters.CharFilter(field_name="name", label=section_label, lookup_expr='icontains')
        self.filters['division'] = django_filters.ChoiceFilter(field_name="division", label=division_label,
                                                               lookup_expr='exact', choices=division_choices)
        self.filters['branch'] = django_filters.ChoiceFilter(field_name="division__branch", label=branch_label,
                                                             lookup_expr='exact', choices=branch_choices)
        self.filters['region'] = django_filters.ChoiceFilter(field_name="division__branch__region", label=region_label,
                                                             lookup_expr='exact', choices=region_choices)

        try:
            # if there is a filter on region, filter the division and section filter accordingly
            if self.data["region"] != "":
                my_region_id = int(self.data["region"])
                division_choices = utils.get_division_choices(region_filter=my_region_id)
                self.filters['division'] = django_filters.ChoiceFilter(field_name="division", label=division_label,
                                                                       lookup_expr='exact', choices=division_choices)
                branch_choices = utils.get_branch_choices(region_filter=my_region_id)
                self.filters['branch'] = django_filters.ChoiceFilter(field_name="division__branch", label=branch_label,
                                                                     lookup_expr='exact', choices=branch_choices)

            # if there is a filter on branch, filter the division
            if self.data["branch"] != "":
                my_branch_id = int(self.data["branch"])
                division_choices = utils.get_division_choices(branch_filter=my_branch_id)
                self.filters['division'] = django_filters.ChoiceFilter(field_name="division", label=division_label,
                                                                       lookup_expr='exact', choices=division_choices)

        except KeyError:
            print('no data in filter')


class DivisionFilter(django_filters.FilterSet):
    division = django_filters.ChoiceFilter(field_name='name')
    branch = django_filters.ChoiceFilter(field_name='branch')
    region = django_filters.ChoiceFilter(field_name="branch__region")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region_label = _("Region - Sector (NCR)")
        branch_label = _("Branch - Directorate (NCR)")
        division_label = _("Division - Branch (NCR)")

        region_choices = utils.get_region_choices()
        branch_choices = utils.get_branch_choices()

        self.filters['division'] = django_filters.CharFilter(field_name="name", label=division_label, lookup_expr='icontains')
        self.filters['branch'] = django_filters.ChoiceFilter(field_name="branch", label=branch_label,
                                                             lookup_expr='exact', choices=branch_choices)
        self.filters['region'] = django_filters.ChoiceFilter(field_name="branch__region", label=region_label,
                                                             lookup_expr='exact', choices=region_choices)

        try:
            # if there is a filter on region, filter the division and section filter accordingly
            if self.data["region"] != "":
                my_region_id = int(self.data["region"])
                branch_choices = utils.get_branch_choices(region_filter=my_region_id)
                self.filters['branch'] = django_filters.ChoiceFilter(field_name="branch", label=branch_label,
                                                                     lookup_expr='exact', choices=branch_choices)


        except KeyError:
            print('no data in filter')



class BranchFilter(django_filters.FilterSet):
    branch = django_filters.ChoiceFilter(field_name='name')
    region = django_filters.ChoiceFilter(field_name="division__branch__region")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region_label = _("Region - Sector (NCR)")
        branch_label = _("Branch - Directorate (NCR)")
        region_choices = utils.get_region_choices()
        self.filters['branch'] = django_filters.CharFilter(field_name="name", label=branch_label, lookup_expr='icontains')
        self.filters['region'] = django_filters.ChoiceFilter(field_name="region", label=region_label,
                                                             lookup_expr='exact', choices=region_choices)

