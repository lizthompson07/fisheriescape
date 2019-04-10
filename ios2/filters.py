from django.contrib.auth.models import User
from shared_models import models as shared_models

from . import models
import django_filters


class InstrumentFilter(django_filters.FilterSet):
    # FY_CHOICES = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
    # DIVISION_CHOICES = [(d.id, str(d)) for d in shared_models.Division.objects.filter(branch=1)]
    # SECTION_CHOICES = [(s.id, str(s)) for s in shared_models.Section.objects.filter(division__branch=1)]
    # TYPE_CHOICES = [('CTD', 'CTD'), ('ADCP', 'ADCP'), ('OXY', 'OXY')]
    TYPE_CHOICES = models.Instrument.TYPE_CHOICES
    YES_NO_CHOICES = [(True, "Yes"), (False, "No"), ]

    project_title = django_filters.CharFilter(field_name='project_title', lookup_expr='icontains')
    instrument_type = django_filters.ChoiceFilter(field_name='instrument_type', lookup_expr='exact', choices=TYPE_CHOICES)
    # fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=FY_CHOICES)
    # division = django_filters.ChoiceFilter(field_name='section__division', lookup_expr='exact', label="Division", choices=DIVISION_CHOICES)
    # section = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', label="Section", choices=SECTION_CHOICES)
    submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label="Submitted?", choices=YES_NO_CHOICES)


class MooringFilter(django_filters.FilterSet):
    # FY_CHOICES = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
    # DIVISION_CHOICES = [(d.id, str(d)) for d in shared_models.Division.objects.filter(branch=1)]
    # SECTION_CHOICES = [(s.id, str(s)) for s in shared_models.Section.objects.filter(division__branch=1)]
    # TYPE_CHOICES = [('CTD', 'CTD'), ('ADCP', 'ADCP')]
    YES_NO_CHOICES = [(True, "Yes"), (False, "No"), ]

    mooring = django_filters.CharFilter(field_name='mooring', lookup_expr='icontains')
    mooring_number = django_filters.CharFilter(field_name='mooring_number', lookup_expr='exact')
    # mooring = django_filters.CharFilter(field_name='mooring', lookup_expr='icontains')
    # mooring_number = django_filters.ModelChoiceFilter(queryset=Deployment.objects.all)#, lookup_expr='exact')
    # fiscal_year = django_filters.ChoiceFilter(field_name='year', lookup_expr='exact', choices=FY_CHOICES)
    # division = django_filters.ChoiceFilter(field_name='section__division', lookup_expr='exact', label="Division", choices=DIVISION_CHOICES)
    # section = django_filters.ChoiceFilter(field_name='section', lookup_expr='exact', label="Section", choices=SECTION_CHOICES)
    submitted = django_filters.ChoiceFilter(field_name='submitted', lookup_expr='exact', label="Submitted?", choices=YES_NO_CHOICES)
