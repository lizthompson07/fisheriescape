# from accounts import models as account_models
from django import forms
import django_filters
from . import choices
from . import models

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)
attr_chosen = {"class": "chosen-select"}
attr_chosen_contains = {"class": "chosen-select-contains"}
multi_SelectMultiple_js = {"class": "multi-select"}


class OrganizationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search name", lookup_expr='icontains', widget=forms.TextInput())
    organization_type = django_filters.MultipleChoiceFilter(choices=choices.ORGANIZATION_TYPE, widget=forms.SelectMultiple(attr_chosen))
    province_state = django_filters.MultipleChoiceFilter(choices=choices.PROVINCE_STATE_CHOICES, widget=forms.SelectMultiple(attr_chosen))
    country = django_filters.MultipleChoiceFilter(choices=choices.COUNTRY_CHOICES, widget=forms.SelectMultiple(attr_chosen))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PersonFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search", lookup_expr='icontains', widget=forms.TextInput())
    province_state = django_filters.MultipleChoiceFilter(choices=choices.PROVINCE_STATE_CHOICES, widget=forms.SelectMultiple(attr_chosen))
    role = django_filters.MultipleChoiceFilter(choices=choices.ROLE, widget=forms.SelectMultiple(attr_chosen))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProjectFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(label="Search Name", lookup_expr='icontains', widget=forms.TextInput())
    project_description = django_filters.CharFilter(label="Search Project Description", lookup_expr='icontains', widget=forms.TextInput())
    species = django_filters.ModelMultipleChoiceFilter(field_name='river__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')
    area = django_filters.MultipleChoiceFilter(choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    ecosystem_type = django_filters.ModelMultipleChoiceFilter(queryset=models.EcosystemType.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Ecosystem Type')
    project_type = django_filters.MultipleChoiceFilter(choices=choices.PROJECT_TYPE, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Project Type')
    monitoring_approach = django_filters.ModelMultipleChoiceFilter(queryset=models.MonitoringApproach.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Monitoring Approach')
    government_organization = django_filters.MultipleChoiceFilter(choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    funding_year = django_filters.MultipleChoiceFilter(field_name='funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='CU Name')
    project_stage = django_filters.MultipleChoiceFilter(choices=choices.PROJECT_STAGE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Project Stage")
    project_sub_type = django_filters.ModelMultipleChoiceFilter(queryset=models.ProjectSubType.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    project_theme = django_filters.ModelMultipleChoiceFilter(queryset=models.ProjectTheme.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    core_component = django_filters.ModelMultipleChoiceFilter(queryset=models.CoreComponent.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    supportive_component = django_filters.ModelMultipleChoiceFilter(queryset=models.SupportiveComponent.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    class Meta:
        model = models.Project
        fields = ['project_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ObjectiveFilter(django_filters.FilterSet):
    task_description = django_filters.CharFilter(label='Search Task Description', lookup_expr='icontains', widget=forms.TextInput())
    expected_results = django_filters.CharFilter(label='Search Expected Results', lookup_expr='icontains', widget=forms.TextInput())
    element_title = django_filters.CharFilter(label='Search Element Title', lookup_expr='icontains', widget=forms.TextInput())
    dfo_report = django_filters.CharFilter(label='Search DFO Report', lookup_expr='icontains', widget=forms.TextInput())
    species = django_filters.ModelMultipleChoiceFilter(field_name='location__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')
    objective_category = django_filters.ModelMultipleChoiceFilter(queryset=models.ObjectiveCategory.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    sample_outcome = django_filters.MultipleChoiceFilter(field_name='sample_outcome__sampling_outcome', widget=forms.SelectMultiple(attr_chosen), choices=choices.SAMPLE_TYPE_OUTCOMES, lookup_expr='icontains', label='Sampling Outcome')
    location = django_filters.ModelMultipleChoiceFilter(queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MethodFilter(django_filters.FilterSet):
    planning_method_type = django_filters.MultipleChoiceFilter(choices=choices.PLANNING_METHOD, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Planning Method Type")
    field_work_method_type = django_filters.MultipleChoiceFilter(choices=choices.FIELD_WORK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Field Work Method Type")
    sample_processing_method_type = django_filters.MultipleChoiceFilter(choices=choices.SAMPLE_PROCESSING, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Sample Processing Method Type")
    river = django_filters.ModelMultipleChoiceFilter(field_name='project__river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DataFilter(django_filters.FilterSet):
    species = django_filters.ModelMultipleChoiceFilter(field_name='river__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')
    samples_collected = django_filters.MultipleChoiceFilter(choices=choices.SAMPLE_TYPE_OUTCOMES, widget=forms.SelectMultiple(attr_chosen),lookup_expr='icontains', label="Samples Collected")
    data_products = django_filters.MultipleChoiceFilter(choices=choices.DATA_PRODUCTS, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Data Products")
    samples_collected_database = django_filters.MultipleChoiceFilter(choices=choices.DATABASE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Samples Collected Database")
    data_products_database = django_filters.MultipleChoiceFilter(choices=choices.DATABASE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Data Products Database")
    sample_format = django_filters.MultipleChoiceFilter(choices=choices.SAMPLE_FORMAT, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Sample Format")
    river = django_filters.ModelMultipleChoiceFilter(field_name='river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')

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
    document_name = django_filters.CharFilter(label="Search Document Names", lookup_expr='icontains',widget=forms.TextInput())
    report_timeline = django_filters.MultipleChoiceFilter(choices=choices.REPORT_TIMELINE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Report Timeline')
    report_type = django_filters.MultipleChoiceFilter(choices=choices.REPORT_TYPE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains')
    river = django_filters.ModelMultipleChoiceFilter(field_name='project__river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), label='Area')
    species = django_filters.ModelMultipleChoiceFilter(field_name='project__river__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FeedbackFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Feedback
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)