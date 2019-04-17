from django import forms
from shared_models import models as shared_models
import django_filters


class LineObjectFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search line object (code, term, etc...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class ProjectFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search project (code, name...)",
                                            lookup_expr='icontains', widget=forms.TextInput())


class TransactionFilter(django_filters.FilterSet):
    fiscal_year = django_filters.ChoiceFilter(field_name='fiscal_year', lookup_expr='exact')
    supplier_description = django_filters.CharFilter(field_name='supplier_description', lookup_expr='icontains', label="Supplier description")
    project_code = django_filters.CharFilter(field_name='project__code', lookup_expr='icontains', label="Project code")
    responsibility_center = django_filters.ChoiceFilter(field_name='responsibility_center',
                                                        lookup_expr='exact', label='Responsibility')
    ref_num = django_filters.CharFilter(field_name='reference_number', lookup_expr='icontains', label="Ref. num.")
    in_mrs = django_filters.BooleanFilter(field_name='in_mrs', lookup_expr='exact', label="In MRS?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fy_choices = [(obj.id, "{}".format(obj.full)) for obj in shared_models.FiscalYear.objects.all()]
        rc_choices = [(obj.id, "{} ({})".format(obj.code, obj.name)) for obj in shared_models.ResponsibilityCenter.objects.all()]

        self.filters['fiscal_year'].choices = fy_choices
        self.filters['responsibility_center'].choices = rc_choices

