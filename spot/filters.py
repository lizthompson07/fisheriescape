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
    area = django_filters.MultipleChoiceFilter(choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Region')
    species = django_filters.ModelMultipleChoiceFilter(field_name='river__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')
    river = django_filters.ModelMultipleChoiceFilter(queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='CU Name')
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Sub District Area')
    smu = django_filters.ModelMultipleChoiceFilter(field_name='river__stock_management_unit', queryset=models.StockManagementUnit.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='DU')
    project_type = django_filters.MultipleChoiceFilter(choices=choices.PROJECT_TYPE, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Project Type')
    project_theme = django_filters.ModelMultipleChoiceFilter(queryset=models.ProjectTheme.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    core_component = django_filters.ModelMultipleChoiceFilter(queryset=models.CoreComponent.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    first_nation = django_filters.ModelMultipleChoiceFilter(queryset=models.FirstNations.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    hatchery_name = django_filters.ModelMultipleChoiceFilter(queryset=models.HatcheryName.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    government_organization = django_filters.MultipleChoiceFilter(choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year')
    funding_sources = django_filters.ModelMultipleChoiceFilter(queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    name = django_filters.CharFilter(label="Search Project Name", lookup_expr='icontains', widget=forms.TextInput())
    project_number = django_filters.CharFilter(label="Search Project Number", lookup_expr='icontains', widget=forms.TextInput())
    project_description = django_filters.CharFilter(label="Search Project Description", lookup_expr='icontains', widget=forms.TextInput())
    expected_results = django_filters.CharFilter(field_name='project_objective__task_description', label='Search Expected Results', lookup_expr='icontains', widget=forms.TextInput())
    ecosystem_type = django_filters.ModelMultipleChoiceFilter(queryset=models.EcosystemType.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Ecosystem Type')
    monitoring_approach = django_filters.ModelMultipleChoiceFilter(queryset=models.MonitoringApproach.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Monitoring Approach')
    project_stage = django_filters.MultipleChoiceFilter(choices=choices.PROJECT_STAGE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Project Stage")
    project_sub_type = django_filters.ModelMultipleChoiceFilter(queryset=models.ProjectSubType.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    supportive_component = django_filters.ModelMultipleChoiceFilter(queryset=models.SupportiveComponent.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    project_purpose = django_filters.ModelMultipleChoiceFilter(queryset=models.ProjectPurpose.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ObjectiveFilter(django_filters.FilterSet):
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    location = django_filters.ModelMultipleChoiceFilter(field_name='location', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Location')
    species = django_filters.ModelMultipleChoiceFilter(field_name='location__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='location__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='CU Name')
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='location__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    smu = django_filters.ModelMultipleChoiceFilter(field_name='location__stock_management_unit', queryset=models.StockManagementUnit.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='location__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='DU')
    project_type = django_filters.MultipleChoiceFilter(field_name='project__project_type', choices=choices.PROJECT_TYPE, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Project Type')
    project_theme = django_filters.ModelMultipleChoiceFilter(field_name='project__project_theme', queryset=models.ProjectTheme.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    core_component = django_filters.ModelMultipleChoiceFilter(field_name='project__core_component', queryset=models.CoreComponent.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    government_organization = django_filters.MultipleChoiceFilter(field_name='project__government_organization',choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(field_name='project__lead_organization', choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='project__funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year')
    funding_sources = django_filters.ModelMultipleChoiceFilter(field_name='project__funding_sources', queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    task_description = django_filters.CharFilter(label='Search Task Description', lookup_expr='icontains', widget=forms.TextInput())
    expected_results = django_filters.CharFilter(label='Search Expected Results', lookup_expr='icontains', widget=forms.TextInput())
    element_title = django_filters.CharFilter(label='Search Element Title', lookup_expr='icontains', widget=forms.TextInput())
    dfo_report = django_filters.CharFilter(label='Search Products/Reports to DFO', lookup_expr='icontains', widget=forms.TextInput())
    objective_category = django_filters.ModelMultipleChoiceFilter(queryset=models.ObjectiveCategory.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    sample_outcome = django_filters.MultipleChoiceFilter(field_name='sample_outcome__sampling_outcome', widget=forms.SelectMultiple(attr_chosen), choices=choices.SAMPLE_TYPE_OUTCOMES, lookup_expr='icontains', label='Sampling Outcome')
    report_outcome = django_filters.MultipleChoiceFilter(field_name='report_outcome__reporting_outcome', widget=forms.SelectMultiple(attr_chosen), choices=choices.REPORT_OUTCOMES, lookup_expr='icontains', label='Reporting Outcome')
    sil_requirement = django_filters.ChoiceFilter(choices=choices.YES_NO_UNKNOWN, lookup_expr='icontains')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MethodFilter(django_filters.FilterSet):
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    river = django_filters.ModelMultipleChoiceFilter(field_name='project__river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')
    species = django_filters.ModelMultipleChoiceFilter(field_name='project__river__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='project__river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='CU Name')
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='project__river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    smu = django_filters.ModelMultipleChoiceFilter(field_name='project__river__stock_management_unit', queryset=models.StockManagementUnit.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='project__river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='DU')
    project_type = django_filters.MultipleChoiceFilter(field_name='project__project_type', choices=choices.PROJECT_TYPE, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Project Type')
    project_theme = django_filters.ModelMultipleChoiceFilter(field_name='project__project_theme', queryset=models.ProjectTheme.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    core_component = django_filters.ModelMultipleChoiceFilter(field_name='project__core_component', queryset=models.CoreComponent.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    government_organization = django_filters.MultipleChoiceFilter(field_name='project__government_organization',choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(field_name='project__lead_organization', choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='project__funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year')
    funding_sources = django_filters.ModelMultipleChoiceFilter(field_name='project__funding_sources', queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    planning_method_type = django_filters.MultipleChoiceFilter(choices=choices.PLANNING_METHOD, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Planning Method Type")
    field_work_method_type = django_filters.MultipleChoiceFilter(choices=choices.FIELD_WORK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Field Work Method Type")
    sample_processing_method_type = django_filters.MultipleChoiceFilter(choices=choices.SAMPLE_PROCESSING, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Sample Processing Method Type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DataFilter(django_filters.FilterSet):
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    river = django_filters.ModelMultipleChoiceFilter(field_name='river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')
    species = django_filters.ModelMultipleChoiceFilter(field_name='river__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='CU Name')
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    smu = django_filters.ModelMultipleChoiceFilter(field_name='river__stock_management_unit', queryset=models.StockManagementUnit.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='DU')
    project_type = django_filters.MultipleChoiceFilter(field_name='project__project_type', choices=choices.PROJECT_TYPE, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Project Type')
    project_theme = django_filters.ModelMultipleChoiceFilter(field_name='project__project_theme', queryset=models.ProjectTheme.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    core_component = django_filters.ModelMultipleChoiceFilter(field_name='project__core_component', queryset=models.CoreComponent.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    government_organization = django_filters.MultipleChoiceFilter(field_name='project__government_organization',choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(field_name='project__lead_organization', choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='project__funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year')
    funding_sources = django_filters.ModelMultipleChoiceFilter(field_name='project__funding_sources', queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    samples_collected = django_filters.MultipleChoiceFilter(choices=choices.SAMPLE_TYPE_OUTCOMES, widget=forms.SelectMultiple(attr_chosen),lookup_expr='icontains', label="Samples Collected")
    data_products = django_filters.MultipleChoiceFilter(choices=choices.DATA_PRODUCTS, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Data Products")
    samples_collected_database = django_filters.MultipleChoiceFilter(choices=choices.DATABASE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Samples Collected Database")
    data_products_database = django_filters.MultipleChoiceFilter(choices=choices.DATABASE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Data Products Database")
    sample_format = django_filters.MultipleChoiceFilter(choices=choices.SAMPLE_FORMAT, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Sample Format")

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
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    river = django_filters.ModelMultipleChoiceFilter(field_name='river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')
    species = django_filters.ModelMultipleChoiceFilter(field_name='river__species', queryset=models.Species.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Species')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='CU Name')
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    smu = django_filters.ModelMultipleChoiceFilter(field_name='river__stock_management_unit', queryset=models.StockManagementUnit.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='DU')
    project_type = django_filters.MultipleChoiceFilter(field_name='project__project_type', choices=choices.PROJECT_TYPE, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Project Type')
    project_theme = django_filters.ModelMultipleChoiceFilter(field_name='project__project_theme', queryset=models.ProjectTheme.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    core_component = django_filters.ModelMultipleChoiceFilter(field_name='project__core_component', queryset=models.CoreComponent.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    government_organization = django_filters.MultipleChoiceFilter(field_name='project__government_organization',choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(field_name='project__lead_organization', choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='project__funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year')
    funding_sources = django_filters.ModelMultipleChoiceFilter(field_name='project__funding_sources', queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    document_name = django_filters.CharFilter(label="Search Document Names", lookup_expr='icontains',widget=forms.TextInput())
    report_timeline = django_filters.MultipleChoiceFilter(choices=choices.REPORT_TIMELINE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Report Timeline')
    report_type = django_filters.MultipleChoiceFilter(choices=choices.REPORT_TYPE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FeedbackFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Feedback
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)