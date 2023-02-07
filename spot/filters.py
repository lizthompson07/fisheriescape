# from accounts import models as account_models
from django import forms
import django_filters
from . import choices
from . import models

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)
attr_chosen = {"class": "chosen-select", "placeholder": ''}
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
    # SEARCH #
    name = django_filters.CharFilter(label="Search Project Name", lookup_expr='icontains', widget=forms.TextInput())
    project_number = django_filters.CharFilter(label="Search Project Number", lookup_expr='icontains', widget=forms.TextInput())
    project_description = django_filters.CharFilter(label="Search Project Description", lookup_expr='icontains', widget=forms.TextInput())
    expected_results = django_filters.CharFilter(field_name='project_activity_and_outcome__expected_results', label='Search Expected Results', lookup_expr='icontains', widget=forms.TextInput())

    # GEOGRAPHICAL #
    species = django_filters.MultipleChoiceFilter(field_name='river__species', choices=choices.SPECIES, widget=forms.SelectMultiple(attr_chosen), label='Species')
    river = django_filters.CharFilter(field_name="river__name", lookup_expr='icontains', widget=forms.TextInput(), label='River Search')
    #river = django_filters.ModelMultipleChoiceFilter(queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')
    ecosystem_type = django_filters.ModelMultipleChoiceFilter(queryset=models.EcosystemType.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Ecosystem Type')

    # STOCK ASSESSMENT #
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Sub District Area')
    area = django_filters.MultipleChoiceFilter(choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    smu = django_filters.MultipleChoiceFilter(field_name='river__stock_management_unit', choices=choices.STOCK_MANAGEMENT_UNIT, widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Designatable Unit')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Conservation Unit Name')
    monitoring_approach = django_filters.ModelMultipleChoiceFilter(queryset=models.MonitoringApproach.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Monitoring Approach')

    # PROJECT CLASSIFICATIONS #
    biological_process_type_2 = django_filters.MultipleChoiceFilter(choices=choices.LEVEL_2, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Biological Process Type - level 2')
    biological_process_type_1 = django_filters.MultipleChoiceFilter(choices=choices.LEVEL_1, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Biological Process Type - Level 1')
    activity_type_1 = django_filters.ModelMultipleChoiceFilter(queryset=models.ActivityType1.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    biological_process_type_3 = django_filters.ModelMultipleChoiceFilter(queryset=models.BiologicalProcessType3.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    activity_type_2 = django_filters.ModelMultipleChoiceFilter(queryset=models.ActivityType2.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    activity_type_3 = django_filters.ModelMultipleChoiceFilter(queryset=models.ActivityType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 3')
    project_stage = django_filters.MultipleChoiceFilter(choices=choices.PROJECT_STAGE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Project Stage")
    project_purpose = django_filters.ModelMultipleChoiceFilter(queryset=models.ProjectPurpose.objects.all(), widget=forms.SelectMultiple(attr_chosen))

    # OTHER #
    funding_sources = django_filters.ModelMultipleChoiceFilter(queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen))
    government_organization = django_filters.MultipleChoiceFilter(choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year - Fiscal')
    first_nation = django_filters.ModelMultipleChoiceFilter(queryset=models.FirstNations.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='First Nation')
    hatchery_name = django_filters.ModelMultipleChoiceFilter(queryset=models.HatcheryName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Hatchery Name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ActivitiesAndOutcomesFilter(django_filters.FilterSet):

    project_name = django_filters.CharFilter(field_name='project__name', label="Search Project Name", lookup_expr='icontains', widget=forms.TextInput())
    task_description = django_filters.CharFilter(label='Search Task Description', lookup_expr='icontains', widget=forms.TextInput())
    expected_results = django_filters.CharFilter(label='Search Expected Results', lookup_expr='icontains', widget=forms.TextInput())
    element_title = django_filters.CharFilter(label='Search Element Title', lookup_expr='icontains', widget=forms.TextInput())
    dfo_report = django_filters.CharFilter(label='Search Products/Reports to DFO', lookup_expr='icontains', widget=forms.TextInput())

    # GEOGRAPHICAL #
    species = django_filters.MultipleChoiceFilter(field_name='river__species', choices=choices.SPECIES, widget=forms.SelectMultiple(attr_chosen), label='Species')
    #location = django_filters.ModelMultipleChoiceFilter(field_name='location', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Location')
    river = django_filters.CharFilter(field_name="river__name", lookup_expr='icontains', widget=forms.TextInput(), label='River Search')

    # STOCK ASSESSMENT #
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Sub District Area')
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    smu = django_filters.MultipleChoiceFilter(field_name='river__stock_management_unit', choices=choices.STOCK_MANAGEMENT_UNIT, widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Designatable Unit')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Conservation Unit Name')


    # PROJECT CLASSIFICATIONS #
    biological_process_type_1 = django_filters.MultipleChoiceFilter(field_name='project__biological_process_type_1', choices=choices.LEVEL_1, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Biological Process Type - Level 1')
    activity_type_1 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_1', queryset=models.ActivityType1.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 1')
    biological_process_type_3 = django_filters.ModelMultipleChoiceFilter(field_name='project__biological_process_type_3', queryset=models.BiologicalProcessType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Biological Process Type - level 3')
    activity_type_2 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_2', queryset=models.ActivityType2.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 2')
    activity_type_3 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_3', queryset=models.ActivityType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 3')
    activity_outcome_category = django_filters.ModelMultipleChoiceFilter(queryset=models.ActivityOutcomeCategory.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activities & Outcome Category')

    # OTHER #
    funding_sources = django_filters.ModelMultipleChoiceFilter(field_name='project__funding_sources', queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Funding Sources')
    government_organization = django_filters.MultipleChoiceFilter(field_name='project__government_organization',choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(field_name='project__lead_organization', choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='project__funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year - Fiscal')
    first_nation = django_filters.ModelMultipleChoiceFilter(field_name='project__fist_nation',queryset=models.FirstNations.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='First Nation')
    hatchery_name = django_filters.ModelMultipleChoiceFilter(field_name='project__hatchery_name', queryset=models.HatcheryName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Hatchery Name')
    sample_outcome = django_filters.MultipleChoiceFilter(field_name='sample_outcome__sampling_outcome', widget=forms.SelectMultiple(attr_chosen), choices=choices.SAMPLE_TYPE_OUTCOMES, lookup_expr='icontains', label='Sampling Outcome')
    report_outcome = django_filters.MultipleChoiceFilter(field_name='report_outcome__reporting_outcome', widget=forms.SelectMultiple(attr_chosen), choices=choices.REPORT_OUTCOMES, lookup_expr='icontains', label='Reporting Outcome')
    sil_requirement = django_filters.ChoiceFilter(choices=choices.YES_NO_UNKNOWN, lookup_expr='icontains')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MethodFilter(django_filters.FilterSet):
    project_name = django_filters.CharFilter(field_name='project__name', label="Search Project Name", lookup_expr='icontains', widget=forms.TextInput())
    project_number = django_filters.CharFilter(field_name='project__project_number', label="Search Project Number", lookup_expr='icontains', widget=forms.TextInput())
    project_description = django_filters.CharFilter(field_name='project__project_description', label="Search Project Description", lookup_expr='icontains', widget=forms.TextInput())
    expected_results = django_filters.CharFilter(field_name='project_activity_and_outcome__expected_results', label='Search Expected Results', lookup_expr='icontains', widget=forms.TextInput())

    # GEOGRAPHICAL #
    species = django_filters.MultipleChoiceFilter(field_name='project__river__species', choices=choices.SPECIES, widget=forms.SelectMultiple(attr_chosen), label='Species')
    river = django_filters.CharFilter(field_name="project__river__name", lookup_expr='icontains', widget=forms.TextInput(), label='River Search')
    #river = django_filters.ModelMultipleChoiceFilter(field_name='project__river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')

    # STOCK ASSESSMENT #
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='project__river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Sub District Area')
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    smu = django_filters.MultipleChoiceFilter(field_name='project__river__stock_management_unit', choices=choices.STOCK_MANAGEMENT_UNIT, widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='project__river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Designatable Unit')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='project__river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Conservation Unit Name')

    # PROJECT CLASSIFICATIONS #
    biological_process_type_1 = django_filters.MultipleChoiceFilter(field_name='project__biological_process_type_1', choices=choices.LEVEL_1, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Biological Process Type - level 1')
    activity_type_1 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_1', queryset=models.ActivityType1.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 1')
    biological_process_type_3 = django_filters.ModelMultipleChoiceFilter(field_name='project__biological_process_type_3', queryset=models.BiologicalProcessType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Biological Process Type - level 3')
    activity_type_2 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_2', queryset=models.ActivityType2.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 2')
    activity_type_3 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_3', queryset=models.ActivityType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 3')
    planning_method_type = django_filters.MultipleChoiceFilter(choices=choices.PLANNING_METHOD, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Planning Method Type")
    field_work_method_type = django_filters.MultipleChoiceFilter(choices=choices.FIELD_WORK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Field Work Method Type")
    sample_processing_method_type = django_filters.MultipleChoiceFilter(choices=choices.SAMPLE_PROCESSING, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label="Sample Processing Method Type")

    # OTHER #
    funding_sources = django_filters.ModelMultipleChoiceFilter(field_name='project__funding_sources', queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Funding Sources')
    government_organization = django_filters.MultipleChoiceFilter(field_name='project__government_organization',choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(field_name='project__lead_organization', choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='project__funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year - Fiscal')
    first_nation = django_filters.ModelMultipleChoiceFilter(field_name='project__fist_nation',queryset=models.FirstNations.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='First Nation')
    hatchery_name = django_filters.ModelMultipleChoiceFilter(field_name='project__hatchery_name', queryset=models.HatcheryName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Hatchery Name')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DataFilter(django_filters.FilterSet):

    # SEARCH #
    project_name = django_filters.CharFilter(field_name='project__name', label="Search Project Name", lookup_expr='icontains', widget=forms.TextInput())
    project_number = django_filters.CharFilter(field_name='project__project_number', label="Search Project Number", lookup_expr='icontains', widget=forms.TextInput())
    project_description = django_filters.CharFilter(field_name='project__project_description', label="Search Project Description", lookup_expr='icontains', widget=forms.TextInput())
    expected_results = django_filters.CharFilter(field_name='project_activity_and_outcome__expected_results', label='Search Expected Results', lookup_expr='icontains', widget=forms.TextInput())

    # GEOGRAPHICAL #
    species = django_filters.MultipleChoiceFilter(field_name='river__species', choices=choices.SPECIES, widget=forms.SelectMultiple(attr_chosen), label='Species')
    river = django_filters.CharFilter(field_name="river__name", lookup_expr='icontains', widget=forms.TextInput(), label='Search River')
    #river = django_filters.ModelMultipleChoiceFilter(field_name='river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')

    # STOCK ASSESSMENT #
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Sub District Area')
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    smu = django_filters.MultipleChoiceFilter(field_name='river__stock_management_unit', choices=choices.STOCK_MANAGEMENT_UNIT, widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Designatable Unit')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Conservation Unit Name')

    # PROJECT CLASSIFICATION #
    biological_process_type_1 = django_filters.MultipleChoiceFilter(field_name='project__biological_process_type_1', choices=choices.LEVEL_1, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Biological Process Type - Level 1')
    activity_type_1 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_1', queryset=models.ActivityType1.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 1')
    biological_process_type_3 = django_filters.ModelMultipleChoiceFilter(field_name='project__biological_process_type_3', queryset=models.BiologicalProcessType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Biological Process Type - level 3')
    activity_type_2 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_2', queryset=models.ActivityType2.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 2')
    activity_type_3 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_3', queryset=models.ActivityType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 3')

    # OTHER #
    funding_sources = django_filters.ModelMultipleChoiceFilter(field_name='project__funding_sources', queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Funding Sources')
    government_organization = django_filters.MultipleChoiceFilter(field_name='project__government_organization',choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(field_name='project__lead_organization', choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='project__funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year - Fiscal')
    first_nation = django_filters.ModelMultipleChoiceFilter(field_name='project__fist_nation',queryset=models.FirstNations.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='First Nation')
    hatchery_name = django_filters.ModelMultipleChoiceFilter(field_name='project__hatchery_name', queryset=models.HatcheryName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Hatchery Name')
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

    project_name = django_filters.CharFilter(field_name='project__name', label="Search Project Name", lookup_expr='icontains', widget=forms.TextInput())
    document_name = django_filters.CharFilter(label="Search Document Names", lookup_expr='icontains',widget=forms.TextInput())

    # GEOGRAPHICAL #
    species = django_filters.MultipleChoiceFilter(field_name='river__species', choices=choices.SPECIES, widget=forms.SelectMultiple(attr_chosen), label='Species')
    river = django_filters.CharFilter(field_name="project__river__name", lookup_expr='icontains', widget=forms.TextInput(), label='Search River')
    #river = django_filters.ModelMultipleChoiceFilter(field_name='project__river', queryset=models.River.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='River')

    # STOCK ASSESSMENT #
    sub_district_area = django_filters.ModelMultipleChoiceFilter(field_name='project__river__sub_district_area', queryset=models.SubDistrictArea.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Sub District Area')
    area = django_filters.MultipleChoiceFilter(field_name='project__area', choices=choices.AREA, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Area')
    smu = django_filters.MultipleChoiceFilter(field_name='project__river__stock_management_unit', choices=choices.STOCK_MANAGEMENT_UNIT, widget=forms.SelectMultiple(attr_chosen), label='Stock Management Area')
    du = django_filters.ModelMultipleChoiceFilter(field_name='project__river__du', queryset=models.DU.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Designatable Unit')
    cu_name = django_filters.ModelMultipleChoiceFilter(field_name='project__river__cu_name', queryset=models.CUName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Conservation Unit Name')

    # PROJECT CLASSIFICATIONS #
    biological_process_type_1 = django_filters.MultipleChoiceFilter(field_name='project__biological_process_type_1', choices=choices.LEVEL_1, widget=forms.SelectMultiple(attr_chosen),  lookup_expr='icontains', label='Biological Process Type - Level 1')
    activity_type_1 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_1', queryset=models.ActivityType1.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 1')
    biological_process_type_3 = django_filters.ModelMultipleChoiceFilter(field_name='project__biological_process_type_3', queryset=models.BiologicalProcessType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Biological Process Type - level 3')
    activity_type_2 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_2', queryset=models.ActivityType2.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 2')
    activity_type_3 = django_filters.ModelMultipleChoiceFilter(field_name='project__activity_type_3', queryset=models.ActivityType3.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Activity Type - level 3')
    report_type = django_filters.MultipleChoiceFilter(choices=choices.REPORT_TYPE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains')

    # OTHER #
    funding_sources = django_filters.ModelMultipleChoiceFilter(field_name='project__funding_sources', queryset=models.FundingSources.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Funding Sources')
    government_organization = django_filters.MultipleChoiceFilter(field_name='project__government_organization',choices=choices.GOVERNMENT_LINK, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Link to other Government Departments')
    lead_organization = django_filters.MultipleChoiceFilter(field_name='project__lead_organization', choices=choices.LEAD_ORGANIZATION, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Lead Organization')
    funding_year = django_filters.MultipleChoiceFilter(field_name='project__funding_year__funding_year', widget=forms.SelectMultiple(attr_chosen), choices=choices.FUNDING_YEARS,  lookup_expr='icontains', label='Funding Year - Fiscal ')
    first_nation = django_filters.ModelMultipleChoiceFilter(field_name='project__fist_nation',queryset=models.FirstNations.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='First Nation')
    hatchery_name = django_filters.ModelMultipleChoiceFilter(field_name='project__hatchery_name', queryset=models.HatcheryName.objects.all(), widget=forms.SelectMultiple(attr_chosen), label='Hatchery Name')
    report_timeline = django_filters.MultipleChoiceFilter(choices=choices.REPORT_TIMELINE, widget=forms.SelectMultiple(attr_chosen), lookup_expr='icontains', label='Report Timeline')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FeedbackFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = models.Feedback
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)