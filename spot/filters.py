# from accounts import models as account_models
from gettext import gettext as _
from django import forms
import django_filters
from django.db.models import Q

from . import models
from masterlist import models as ml_models
from shared_models import models as shared_models
from sar_search import models as sar_models

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search name", lookup_expr='icontains', widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search", lookup_expr='icontains', widget=forms.TextInput())

    org = django_filters.ModelChoiceFilter(field_name='organization', lookup_expr='exact', queryset=models.Organization.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProjectFilter(django_filters.FilterSet):

    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    species = django_filters.ModelChoiceFilter(field_name='target_species', lookup_expr='exact', queryset=models.Species.objects.all())
    regions = django_filters.ModelChoiceFilter(field_name='region', lookup_expr='exact', queryset=models.Region.objects.all())
    cu = django_filters.ModelChoiceFilter(field_name='cu_name', lookup_expr='exact', queryset=models.CUName.objects.all())
    smu = django_filters.ModelChoiceFilter(field_name='smu_name', lookup_expr='exact', queryset=models.SMUCode.objects.all())
    project_development_phase = django_filters.ModelChoiceFilter(field_name='project_stage', lookup_expr='exact', queryset=models.ProjectStage.objects.all())
    project_scale = django_filters.ModelChoiceFilter(field_name='project_scale', lookup_expr='exact', queryset=models.ProjectScale.objects.all())
    project_type = django_filters.ModelChoiceFilter(field_name='project_type', lookup_expr='exact', queryset=models.ProjectType.objects.all())
    project_sub_type = django_filters.ModelChoiceFilter(field_name='project_sub_type', lookup_expr='exact', queryset=models.ProjectSubType.objects.all())
    monitoring_approach = django_filters.ModelChoiceFilter(field_name='monitoring_approach', lookup_expr='exact', queryset=models.MonitoringApproach.objects.all())
    project_theme = django_filters.ModelChoiceFilter(field_name='project_theme', lookup_expr='exact', queryset=models.ProjectTheme.objects.all())
    core_component = django_filters.ModelChoiceFilter(field_name='core_component', lookup_expr='exact', queryset=models.CoreComponent.objects.all())
    supportive_component = django_filters.ModelChoiceFilter(field_name='supportive_component', lookup_expr='exact', queryset=models.SupportComponent.objects.all())
    government_programs = django_filters.ModelChoiceFilter(field_name='government_organization', lookup_expr='exact', queryset=models.LinkedGovernmentOrganizations.objects.all())
    dfo_programs = django_filters.ModelChoiceFilter(field_name='DFO_link', lookup_expr='exact', queryset=models.DFOLink.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ObjectiveFilter(django_filters.FilterSet):

    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MethodFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DatabaseFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MeetingsFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReportsFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains',widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FeedbackFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)