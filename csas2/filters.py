import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _

from shared_models.models import FiscalYear, Division, Section, Branch, Region, Person
from . import models, utils



class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = Person
        fields = {
            'last_name': ['exact'],
            'affiliation': ['icontains'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["last_name"] = django_filters.CharFilter(field_name='search_term', label=_("Any part of name or email"),
                                                              lookup_expr='icontains', widget=forms.TextInput())



class CSASRequestFilter(django_filters.FilterSet):
    request_id = django_filters.NumberFilter(field_name='id', lookup_expr='exact')
    search_term = django_filters.CharFilter(field_name='search_term', lookup_expr='icontains', label=_("Title contains"))
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact')
    region = django_filters.ChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact')
    branch = django_filters.ChoiceFilter(field_name="section__division__branch", label=_("Branch / Sector"), lookup_expr='exact')
    has_process = django_filters.BooleanFilter(field_name='process', lookup_expr='isnull', label=_("Has process?"), exclude=True)

    class Meta:
        model = models.CSASRequest
        fields = {
            'status': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        region_choices = utils.get_region_choices()
        branch_choices = utils.get_branch_choices()
        fy_choices = [(fy.id, str(fy)) for fy in FiscalYear.objects.filter(csas_requests__isnull=False)]

        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact', choices=fy_choices, label=_("Fiscal year"))
        self.filters['region'] = django_filters.ChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact',
                                                             choices=region_choices)
        self.filters['branch'] = django_filters.ChoiceFilter(field_name="section__division__branch", label=_("Branch / Sector"), lookup_expr='exact',
                                                               choices=branch_choices)

        try:
            if self.data["region"] != "":
                my_region_id = int(self.data["region"])
                branch_choices = [my_set for my_set in utils.get_branch_choices() if Branch.objects.get(pk=my_set[0]).region_id == my_region_id]
                self.filters['branch'] = django_filters.ChoiceFilter(field_name="section__division__branch", label=_("Branch / Sector"), lookup_expr='exact',
                                                                       choices=branch_choices)

                section_choices = [my_set for my_set in utils.get_section_choices() if
                                   Section.objects.get(pk=my_set[0]).division.branch.region_id == my_region_id]

        except KeyError:
            print('no data in filter')



class ProcessFilter(django_filters.FilterSet):
    process_id = django_filters.NumberFilter(field_name='id', lookup_expr='exact')
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact')
    search_term = django_filters.CharFilter(field_name='search_term', lookup_expr='icontains', label=_("Title contains"))
    lead_region = django_filters.ChoiceFilter(field_name="lead_region", label=_("Lead Region"), lookup_expr='exact')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fy_choices = [(fy.id, str(fy)) for fy in FiscalYear.objects.filter(csas_requests__isnull=False)]
        region_choices = [(obj.id, str(obj)) for obj in Region.objects.filter(process_lead_regions__isnull=False).distinct()]

        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=fy_choices, label=_("Fiscal year"))
        self.filters['lead_region'] = django_filters.ChoiceFilter(field_name="lead_region", label=_("Lead Region"), lookup_expr='exact', choices=region_choices)


class MeetingFilter(django_filters.FilterSet):
    process = django_filters.ChoiceFilter(field_name='process', lookup_expr='exact')
    search_term = django_filters.CharFilter(field_name='search_term', lookup_expr='icontains', label=_("Title contains"))
    region = django_filters.ChoiceFilter(field_name="section__division__branch__region", label=_("Region"), lookup_expr='exact')
    branch = django_filters.ChoiceFilter(field_name="section__division__branch", label=_("Branch / Sector"), lookup_expr='exact')
    has_process = django_filters.BooleanFilter(field_name='process', lookup_expr='isnull', label=_("Has process?"), exclude=True)



class DocumentFilter(django_filters.FilterSet):
    class Meta:
        model = models.Document
        fields = {
            'id': ['exact'],
            'type': ['exact'],
            'status': ['exact'],
            'process': ['exact'],
            'series': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["id"] = django_filters.CharFilter(field_name='search_term', label=_("Title contains"),
                                                              lookup_expr='icontains', widget=forms.TextInput())


