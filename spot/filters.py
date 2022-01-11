# from accounts import models as account_models
from django import forms
import django_filters
from . import choices
from . import models

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search name", lookup_expr='icontains', widget=forms.TextInput())
    organization_type = django_filters.ChoiceFilter(choices=choices.ORGANIZATION_TYPE)
    province_state = django_filters.ChoiceFilter(choices=choices.PROVINCE_STATE_CHOICES)
    country = django_filters.ChoiceFilter(choices=choices.COUNTRY_CHOICES)

    class Meta:
        model = models.Organization
        fields = ['organization_type', 'province_state', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search", lookup_expr='icontains', widget=forms.TextInput())
    province = django_filters.ChoiceFilter(choices=choices.PROVINCE_STATE_CHOICES)
    role = django_filters.ChoiceFilter(choices=choices.ROLE)

    class Meta:
        model = models.Person
        fields = ['province', 'organizations', 'role',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProjectFilter(django_filters.FilterSet):

    #search_term = django_filters.CharFilter(field_name='search_term', label="Search", lookup_expr='icontains', widget=forms.TextInput())
    region = django_filters.ChoiceFilter(choices=choices.REGION, lookup_expr='icontains')
    stock_management_unit = django_filters.ChoiceFilter(choices=choices.SMU_NAME, lookup_expr='icontains')
    project_stage = django_filters.ChoiceFilter(choices=choices.PROJECT_STAGE, lookup_expr='icontains')
    ecosystem_type = django_filters.ChoiceFilter(choices=choices.ECOSYSTEM_TYPE, lookup_expr='icontains')
    project_type = django_filters.ChoiceFilter(choices=choices.PROJECT_TYPE, lookup_expr='icontains')
    monitoring_approach = django_filters.ChoiceFilter(choices=choices.MONITORING_APPROACH, lookup_expr='icontains')
    government_organization = django_filters.ChoiceFilter(choices=choices.GOVERNMENT_LINK, lookup_expr='icontains')
    DFO_link = django_filters.ChoiceFilter(choices=choices.DFO_LINK, lookup_expr='icontains')

    class Meta:
        model = models.Project
        fields = ['species', 'region', 'cu_name', 'stock_management_unit', 'project_stage','ecosystem_type',
                  'project_type', 'project_sub_type', 'monitoring_approach',
                  'project_theme', 'core_component', 'supportive_component',
                  'government_organization', 'DFO_link',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ObjectiveFilter(django_filters.FilterSet):

    #search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Objective
        fields = ['species', 'objective_category', 'location',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MethodFilter(django_filters.FilterSet):
    #search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Method
        fields = ['planning_method_type', 'field_work_method_type', 'sample_processing_method_type',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DataFilter(django_filters.FilterSet):
    #search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Data
        fields = ['species', 'samples_collected', 'data_products', 'samples_collected_database', 'data_products_database', 'sample_format', 'data_programs',]

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
    #search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains',widget=forms.TextInput())
    report_timeline = django_filters.ChoiceFilter(choices=choices.REPORT_TIMELINE)
    report_type = django_filters.ChoiceFilter(choices=choices.REPORT_TYPE)


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