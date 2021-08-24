import django_filters
from django.utils.translation import gettext_lazy as _

from . import models
from . import utils

chosen_js = {"class": "chosen-select-contains"}


class SectionFilter(django_filters.FilterSet):
    section = django_filters.ChoiceFilter(field_name='name')
    division = django_filters.ChoiceFilter(field_name='division')
    branch = django_filters.ChoiceFilter(field_name='division__branch')
    sector = django_filters.ChoiceFilter(field_name='division__branch__sector')
    region = django_filters.ChoiceFilter(field_name="division__branch__sector__region")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region_label = _("Region - National (NCR)")
        sector_label = _("Sector")
        branch_label = _("Branch - Directorate (NCR)")
        division_label = _("Division - Branch (NCR)")
        section_label = _("Section - Team (NCR)")
        region_choices = utils.get_region_choices()
        sector_choices = utils.get_sector_choices()
        branch_choices = utils.get_branch_choices()
        division_choices = utils.get_division_choices()

        self.filters['section'] = django_filters.CharFilter(field_name="name", label=section_label, lookup_expr='icontains')
        self.filters['division'] = django_filters.ChoiceFilter(field_name="division", label=division_label,
                                                               lookup_expr='exact', choices=division_choices)
        self.filters['branch'] = django_filters.ChoiceFilter(field_name="division__branch", label=branch_label,
                                                             lookup_expr='exact', choices=branch_choices)
        self.filters['sector'] = django_filters.ChoiceFilter(field_name="division__branch__sector", label=sector_label,
                                                             lookup_expr='exact', choices=sector_choices)
        self.filters['region'] = django_filters.ChoiceFilter(field_name="division__branch__sector__region", label=region_label,
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
                sector_choices = utils.get_sector_choices(region_filter=my_region_id)
                self.filters['sector'] = django_filters.ChoiceFilter(field_name="division__branch__sector", label=sector_label,
                                                                     lookup_expr='exact', choices=sector_choices)

            # if there is a filter on sector, filter the branch, division
            if self.data["sector"] != "":
                my_sector_id = int(self.data["sector"])
                branch_choices = utils.get_branch_choices(sector_filter=my_sector_id)
                self.filters['branch'] = django_filters.ChoiceFilter(field_name="division__branch", label=branch_label,
                                                                     lookup_expr='exact', choices=branch_choices)
                division_choices = utils.get_division_choices(sector_filter=my_sector_id)
                self.filters['division'] = django_filters.ChoiceFilter(field_name="division", label=division_label,
                                                                       lookup_expr='exact', choices=division_choices)

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
        region_label = _("Region - National (NCR)")
        sector_label = _("Sector")
        branch_label = _("Branch - Directorate (NCR)")
        division_label = _("Division - Branch (NCR)")

        region_choices = utils.get_region_choices()
        sector_choices = utils.get_sector_choices()
        branch_choices = utils.get_branch_choices()

        self.filters['division'] = django_filters.CharFilter(field_name="name", label=division_label, lookup_expr='icontains')
        self.filters['sector'] = django_filters.ChoiceFilter(field_name="sector", label=sector_label,
                                                             lookup_expr='exact', choices=sector_choices)
        self.filters['branch'] = django_filters.ChoiceFilter(field_name="sector__branch", label=branch_label,
                                                             lookup_expr='exact', choices=branch_choices)
        self.filters['region'] = django_filters.ChoiceFilter(field_name="sector__branch__region", label=region_label,
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
    sector = django_filters.ChoiceFilter(field_name="sector")
    region = django_filters.ChoiceFilter(field_name="sector__region")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region_label = _("Region - National")
        sector_label = _("Sector")
        branch_label = _("Branch - Directorate (NCR)")
        region_choices = utils.get_region_choices()
        sector_choices = utils.get_sector_choices()
        self.filters['branch'] = django_filters.CharFilter(field_name="name", label=branch_label, lookup_expr='icontains')
        self.filters['region'] = django_filters.ChoiceFilter(field_name="region", label=region_label,
                                                             lookup_expr='exact', choices=region_choices)
        self.filters['sector'] = django_filters.ChoiceFilter(field_name="sector__region", label=sector_label,
                                                             lookup_expr='exact', choices=sector_choices)


class SectorFilter(django_filters.FilterSet):
    sector = django_filters.ChoiceFilter(field_name='name')
    region = django_filters.ChoiceFilter(field_name="region")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region_label = _("Region - National (NCR)")
        sector_label = _("Sector")
        region_choices = utils.get_region_choices()
        self.filters['sector'] = django_filters.CharFilter(field_name="name", label=sector_label, lookup_expr='icontains')
        self.filters['region'] = django_filters.ChoiceFilter(field_name="region", label=region_label,
                                                             lookup_expr='exact', choices=region_choices)


class ProjectCodeFilter(django_filters.FilterSet):
    class Meta:
        model = models.Project
        fields = {
            'name': ['icontains'],
            'code': ['icontains'],
        }


class RCFilter(django_filters.FilterSet):
    class Meta:
        model = models.ResponsibilityCenter
        fields = {
            'name': ['icontains'],
            'code': ['icontains'],
        }
