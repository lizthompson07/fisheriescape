# from accounts import models as account_models
from django import forms
import django_filters


from . import models

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search name", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Organization
        fields = ['organization_type', 'province', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Person
        fields = ['province', 'organizations', 'role',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProjectFilter(django_filters.FilterSet):

    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Project
        fields = ['species', 'region', 'cu_name', 'smu_name', 'project_stage','ecosystem_type',
                  'project_type', 'project_sub_type', 'monitoring_approach',
                  'project_theme', 'core_component', 'supportive_component',
                  'government_organization', 'DFO_link',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ObjectiveFilter(django_filters.FilterSet):

    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Objective
        fields = ['species', 'objective_category',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MethodFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Method
        fields = ['planning_method_type', 'field_work_method_type', 'sample_processing_method_type', 'data_entry_method_type',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DataFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Data
        fields = ['species_data', 'samples_collected', 'data_products', 'data_products_database', 'sample_format', 'data_programs',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MeetingsFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Meetings
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReportsFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains',widget=forms.TextInput())

    class Meta:
        model = models.Reports
        fields = ['report_timeline', 'report_type', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FeedbackFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Feedback
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)