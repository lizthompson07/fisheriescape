import django_filters
from django.utils.translation import gettext_lazy as _

from shared_models.models import FiscalYear, Division, Section
from . import models, utils


class CSASRequestFilter(django_filters.FilterSet):
    request_id = django_filters.NumberFilter(field_name='id', lookup_expr='exact')
    fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact')
    search_term = django_filters.CharFilter(field_name='search_term', lookup_expr='icontains', label=_("Title"))
    region = django_filters.ChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact')
    division = django_filters.ChoiceFilter(field_name='section__division', lookup_expr='exact', label=_("Division"))
    section = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', label=_("Section"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        region_choices = utils.get_region_choices()
        division_choices = utils.get_division_choices()
        section_choices = utils.get_section_choices()
        fy_choices = [(fy.id, str(fy)) for fy in FiscalYear.objects.filter(csas_requests__isnull=False)]

        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices, label=_("Fiscal year"))
        self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"), lookup_expr='exact', choices=section_choices)
        self.filters['region'] = django_filters.ChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact',
                                                             choices=region_choices)
        self.filters['division'] = django_filters.ChoiceFilter(field_name="section__division", label=_("Division"), lookup_expr='exact',
                                                               choices=division_choices)

        try:
            if self.data["region"] != "":
                my_region_id = int(self.data["region"])
                division_choices = [my_set for my_set in utils.get_division_choices() if Division.objects.get(pk=my_set[0]).branch.region_id == my_region_id]
                self.filters['division'] = django_filters.ChoiceFilter(field_name="section__division", label=_("Division"), lookup_expr='exact',
                                                                       choices=division_choices)

                section_choices = [my_set for my_set in utils.get_section_choices() if
                                   Section.objects.get(pk=my_set[0]).division.branch.region_id == my_region_id]
                self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"), lookup_expr='exact', choices=section_choices)

            # if there is a filter on division, filter the section filter accordingly
            if self.data["division"] != "":
                my_division_id = int(self.data["division"])

                section_choices = [my_set for my_set in utils.get_section_choices() if Section.objects.get(pk=my_set[0]).division_id == my_division_id]
                self.filters['section'] = django_filters.ChoiceFilter(field_name="section", label=_("Section"), lookup_expr='exact', choices=section_choices)

        except KeyError:
            print('no data in filter')
