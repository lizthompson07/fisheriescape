import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _

from shared_models import models as shared_models
from . import models
from . import utils

chosen_js = {"class": "chosen-select-contains"}


class StaffFilter(django_filters.FilterSet):
    fiscal_year = django_filters.ChoiceFilter(field_name='project_year__fiscal_year', lookup_expr='exact')
    region = django_filters.ChoiceFilter(field_name="project_year__project__section__division__branch__region", label=_("Region"), lookup_expr='exact')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        region_choices = utils.get_region_choices()
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projectyear_set.count() > 0]
        yes_no_choices = [(True, "Yes"), (False, "No"), ]
        self.filters['fiscal_year'] = django_filters.ChoiceFilter(field_name='project_year__fiscal_year', lookup_expr='exact', choices=fy_choices)
        self.filters['region'] = django_filters.ChoiceFilter(field_name="project_year__project__section__division__branch__region", label=_("Region"),
                                                             lookup_expr='exact', choices=region_choices)
        # self.filters['project_year__submitted'].label = "Has the project been submitted?"

    class Meta:
        model = models.Staff
        fields = {
            # 'employee_type': ['exact'],
            'is_lead': ['exact'],
        }


class FunctionalGroupFilter(django_filters.FilterSet):
    class Meta:
        model = models.FunctionalGroup
        fields = {
            'name': ['exact'],
            'theme': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projectyear_set.exists()]
        self.filters['name'] = django_filters.CharFilter(field_name='search_term', label=_("Name"), lookup_expr='icontains',
                                                         widget=forms.TextInput())


class UserFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label=_("Name contains"), lookup_expr='icontains',
                                            widget=forms.TextInput())


class ProjectFilter(django_filters.FilterSet):
    class Meta:
        model = models.Project
        fields = {
            'fiscal_years': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("queryset"):
            fy_ids = [py.fiscal_year_id for py in models.ProjectYear.objects.filter(project__in=kwargs.get("queryset"))]
            fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.filter(id__in=fy_ids)]
        else:
            fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all() if fy.projectyear_set.exists()]
        self.filters['fiscal_years'] = django_filters.ChoiceFilter(field_name='fiscal_years', label=_("Fiscal year"), widget=forms.Select(), choices=fy_choices)


class ProjectYearChildFilter(django_filters.FilterSet):
    project_year = django_filters.NumberFilter(field_name='project_year')
    project = django_filters.NumberFilter(field_name='project_year__project')
    year = django_filters.NumberFilter(field_name='project_year__fiscal_year')
    region_name = django_filters.CharFilter(field_name='project_year__project__section__division__branch__region__name', lookup_expr="icontains")


class DMAFilter(django_filters.FilterSet):
    project = django_filters.NumberFilter(field_name='project')
    fiscal_year = django_filters.NumberFilter(field_name='fiscal_year')
    title_name = django_filters.CharFilter(field_name='title', lookup_expr="icontains")


class ProjectYearFilter(django_filters.FilterSet):
    is_hidden = django_filters.CharFilter(field_name='project__is_hidden')
    status = django_filters.NumberFilter(field_name='status')
    title = django_filters.CharFilter(field_name='project__title', lookup_expr="icontains")
    id = django_filters.NumberFilter(field_name='project__id')
    staff = django_filters.CharFilter(field_name='project__staff_search_field', lookup_expr="icontains")
    fiscal_year = django_filters.NumberFilter(field_name='fiscal_year')
    tag = django_filters.NumberFilter(field_name='project__tags')
    theme = django_filters.NumberFilter(field_name='project__functional_group__theme')
    functional_group = django_filters.NumberFilter(field_name='project__functional_group')
    funding_source = django_filters.NumberFilter(field_name='project__default_funding_source')
    region = django_filters.NumberFilter(field_name='project__section__division__branch__sector__region')
    division = django_filters.NumberFilter(field_name='project__section__division')
    section = django_filters.NumberFilter(field_name='project__section')
    starting_fy = django_filters.NumberFilter(field_name='project__starting_fy')

    has_ship_needs = django_filters.BooleanFilter(field_name="has_ship_needs")
    requires_specialized_equipment = django_filters.BooleanFilter(field_name="requires_specialized_equipment")
    has_field_component = django_filters.BooleanFilter(field_name="has_field_component")
    has_data_component = django_filters.BooleanFilter(field_name="has_data_component")
    has_lab_component = django_filters.BooleanFilter(field_name="has_lab_component")
    requires_abl_services = django_filters.BooleanFilter(field_name="requires_abl_services")

    approval_status = django_filters.NumberFilter(field_name='review__approval_status')
    approval_level = django_filters.NumberFilter(field_name='review__approval_level')
    funding_status = django_filters.NumberFilter(field_name='review__funding_status')

    om_cost_category = django_filters.NumberFilter(field_name='omcost__om_category')
