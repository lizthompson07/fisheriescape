from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _
from . import models
from django.utils.safestring import mark_safe
from . import choices


attr_chosen_contains = {"class": "chosen-select-contains"}
attr_chosen = {"class": "chosen-select"}
attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}
attr_fp_date_time = {"class": "fp-date-time", "placeholder": "Select Date and Time.."}
attr_fp_date_time_email = {"class": "fp-date-time green-borders", "placeholder": "Select Date and Time.."}

multi_select_js = {"class": "multi-select"}
class_editable = {"class": "editable"}

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class OrganizationForm(forms.ModelForm):

    class Meta:
        model = models.Organization #ml
        fields = '__all__'
        widgets = {
            'organization_type': forms.Select(choices=choices.ORGANIZATION_TYPE, attrs=attr_chosen),
            'province_state': forms.Select(choices=choices.PROVINCE_STATE_CHOICES, attrs=attr_chosen),
            'country': forms.Select(choices=choices.COUNTRY_CHOICES, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'name': 'Name of an Organization contributing to the completion of the project',
            'organization_type': 'Type of Organization',
            'section': 'Section, group or sub-department of the original Organization Type',
            'address': 'Number & street information',
            'city': 'City location of organization',
            'province_state': 'Province or State of organization',
            'country': 'Country of organization',
            'phone': 'Primary phone number of organization',
            'email': 'Primary E-mail of organization (reception/admininstration)',
            'website': 'Link to organization website',
        }


class PersonForm(forms.ModelForm):

    class Meta:
        model = models.Person
        fields = '__all__'
        widgets = {
            'organizations': forms.SelectMultiple(attr_chosen),
            'province_state': forms.Select(choices=choices.PROVINCE_STATE_CHOICES, attrs=attr_chosen),
            'country': forms.Select(choices=choices.COUNTRY_CHOICES, attrs=attr_chosen),
            'role': forms.Select(choices=choices.ROLE, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }


class ProjectForm(forms.ModelForm):

    class Meta:
        model = models.Project
        fields = '__all__'
        widgets = {
            'agreement_history': forms.SelectMultiple(attr_chosen),
            'primary_river': forms.Select(attr_chosen),
            'secondary_river': forms.SelectMultiple(attr_chosen),
            'lake_system': forms.SelectMultiple(attr_chosen),
            'watershed': forms.SelectMultiple(attr_chosen),
            'ecosystem_type': forms.Select(choices=choices.ECOSYSTEM_TYPE, attrs=attr_chosen),
            'region': forms.Select(attr_chosen),
            'stock_management_unit': forms.Select(choices=choices.SMU_NAME, attrs=attr_chosen),
            'species': forms.SelectMultiple(multi_select_js),
            'salmon_life_stage': forms.SelectMultiple(multi_select_js),
            'project_stage': forms.Select(choices=choices.PROJECT_STAGE,attrs=attr_chosen),
            'project_type': forms.Select(choices=choices.PROJECT_TYPE, attrs=attr_chosen),
            'project_sub_type': forms.SelectMultiple(multi_select_js),
            'monitoring_approach': forms.Select(choices=choices.MONITORING_APPROACH, attrs=attr_chosen),
            'project_theme': forms.SelectMultiple(multi_select_js),
            'core_component': forms.SelectMultiple(multi_select_js),
            'supportive_component': forms.SelectMultiple(attrs=multi_select_js),
            'project_purpose': forms.SelectMultiple(multi_select_js),
            #'DFO_link': forms.Select(choices=choices.DFO_LINK, attrs=attr_chosen),
            'government_organization': forms.Select(choices=choices.GOVERNMENT_LINK, attrs=attr_chosen),
            'first_nations_contact_role': forms.Select(choices=choices.ROLE, attrs=attr_chosen),
            'agreement_database': forms.Select(choices=choices.AGREEMENT_DATABASE, attrs=attr_chosen),
            'funding_sources': forms.SelectMultiple(attr_chosen),
            'agreement_type': forms.Select(choices=choices.AGREEMENT_TYPE, attrs=attr_chosen),
            'lead_organization': forms.Select(choices=choices.LEAD_ORGANIZATION, attrs=attr_chosen),
            'cu_index': forms.SelectMultiple(attr_chosen),
            'cu_name': forms.Select(attr_chosen),
            'policy_program_connection': forms.Select(choices=choices.POLICY_PROGRAM, attrs=attr_chosen),
            'DFO_project_authority': forms.SelectMultiple(attr_chosen),
            'DFO_area_chief': forms.SelectMultiple(attr_chosen),
            'DFO_aboriginal_AAA': forms.SelectMultiple(attr_chosen),
            'DFO_resource_manager': forms.SelectMultiple(attr_chosen),
            'first_nation': forms.Select(attr_chosen),
            'first_nations_contact': forms.Select(attr_chosen),
            'DFO_technicians': forms.SelectMultiple(attr_chosen),
            'partner': forms.SelectMultiple(attr_chosen),
            'partner_contact': forms.SelectMultiple(attr_chosen),
            'start_date': forms.SelectDateWidget(years=range(1950, 2050)),
            'end_date': forms.SelectDateWidget(years=range(1950, 2050)),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'agreement_database': 'Primary or originating database where the agreement documentation is held',
            'agreement_comment': 'Open Text',
            'funding_sources': 'Funding programs which are contributing funds towards completion of project objectives',
            'other_funding_sources': 'Text relating to any other funding sources not listed above',
            'agreement_type': 'Agreement framework type',
            'project_lead_organization': 'Organization that is taking the primary lead on a project',
            'project_number': 'Number that links individual projects or activities together. GC-AREA-Primary Funding Abbreviation- Agreement Number',
            'agreement_number': 'Original agreement number and activity number',
            'name': 'Name of the project',
            'project_description': 'Brief description of the projects location, species, goals, outcomes',
            'start_date': 'Project start date',
            'end_date': 'Project end date',
            'region': 'Pacific Region where project is primarily taking place',
            'primary_river': 'Chose only one primary river location- linked to Lat/Long',
            'secondary_river': 'Chose many secondary river locations',
            'lake_system': 'Lake system where the project is taking place',
            'ecosystem_type': 'The aquatic ecosystem type(s) where the project takes place',
            'watershed': 'Watershed that the project is located',
            'management_area': 'A large-scale ecosystem-based management unit containing different aquatic environments that are linked by geography, stock composition or environmental conditions',
            'stock_management_unit': 'Salmon Management Unit name',
            'cu_index': 'Conservation Unit Index that is defined by the Wild Salmon Policy',
            'cu_name': 'Conservation Unit Name that is defined by Wild Salmon Policy',
            'species': 'Pacific salmonid species that are involved in the project',
            'salmon_life_stage': 'Life stage of the fish that the project is targetting',
            'project_stage': 'The stage of the project that relates to the implementation timeline',
            'project_type': 'Coarse decription of the project as it relates to either population (i.e. animal-based) or habitat (i.e. environmental) science',
            'project_sub_type': 'Broad category of activity-type that the project relates to',
            'monitoring_approach': 'The relative monitoring effort applied to the project',
            'project_theme': 'A more refined categorization of the project',
            'core_component': 'Category of the ‘major’ elements of a science-based data-collection project',
            'supportive_component': 'Category of the ‘minor’ elements of a science-based data collection project',
            'category_comments': 'Open Text',
            'project_purpose': 'Broad rational as to why the project is being conducted',
            'DFO_link': 'Linkage with other DFO projects (data is collected for or resources shared)',
            'DFO_program_reference': 'Specific reference number and type for program listed above',
            'government_organization': 'Other Government Organizations involved in the project',
            'policy_program_connection': 'DFO Initiatives or Strategic Plans',
            'DFO_project_authority': 'Name of Project Authority',
            'DFO_aboriginal_AAA': 'Aboriginal Affairs Advisor associated with the project',
            'DFO_resource_manager': 'Resource manager associated with the project',
            'first_nation': 'First Nations group associated with the project',
            'first_nations_contact': 'Primary contact for the First Nations group involved with the project',
            'first_nations_contact_role': 'Primary role within the organization (eg. Fisheries Manager)',
            'DFO_technicians': 'Other DFO peronale involved in the project',
            'partner': 'Partner Name associated with the project',
            'partner_contact': 'Primary Contact for Project Partner',
            'contractor': 'Contractor Company Name',
            'contractor_contact': 'Contractor Primary Contact',
        }


class ObjectiveForm(forms.ModelForm):

    class Meta:
        model = models.Objective
        fields = '__all__'
        widgets = {
            'location': forms.SelectMultiple(attr_chosen),
            'project': forms.HiddenInput(),
            'element_title': forms.Select(choices=choices.ELEMENT_TITLE, attrs=attr_chosen),
            'pst_requirement': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'sil_requirement': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'species': forms.SelectMultiple(multi_select_js),
            'objective_category': forms.SelectMultiple(multi_select_js),
            'outcome_barrier': forms.SelectMultiple(multi_select_js),
            'capacity_building': forms.SelectMultiple(multi_select_js),
            'outcome_deadline': forms.DateInput(),
            'outcome_met': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'unique_objective': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'task_description': 'Text from agreement or another summary',
            'element_title': 'Title of the section where the science information is sourced from in the agreement',
            'activity_title': 'Title of the section where the science information is sourced from in the agreement',
            'pst_requirement': 'Yes/No/Unknown',
            'location': 'System Site for the project',
            'species': 'Target Species',
            'objective_category': 'General categorization of what type of sample outcomes are expected',
            'sil_requirement': 'Is a SIL specifically requested in the agreement?',
            'expected_results': 'Text details outlining expected results',
            'dfo_report': 'Text regarding what products or reports that are expected',
            'outcomes_contact': 'Who is reponsible for knowing whether project outcomes have been met',
            'outcome_met': 'Yes/No/Unknown',
            'outcomes_comment': 'Open Text',
            'capacity_building': 'Unintended benefits of the project that will assist in future project operations',
            'outcome_barrier': 'What category of difficulties were encountered towards achieving outcomes?',
            'key_lesson': 'What went right? What went wrong?',
            'missed_opportunities': 'Any area of project management/work that could be identified as a future opportunity',
        }


class MethodForm(forms.ModelForm):
    class Meta:
        model = models.Method
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),
            'planning_method_type': forms.SelectMultiple(multi_select_js),
            'field_work_method_type': forms.SelectMultiple(multi_select_js),
            'sample_processing_method_type': forms.SelectMultiple(multi_select_js),
            'knowledge_consideration': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'planning_method_type': 'Method type linked to the planning aspect of the project',
            'field_work_method_type': 'Methods that relate to the immediate act of carrying out work (counts, tissue collection, temperature etc.)',
            'sample_processing_method_type': 'Data collected in the field that requires further testing, alternation or study (aging, genetics etc.)',
            'scale_processing_location': 'Open Text',
            'otolith_processing_location': 'Open Text',
            'DNA_processing_location': 'Open Text',
            'heads_processing_location': 'Open Text',
            'instrument_data_processing_location': 'Open Text',
            'knowledge_consideration': 'Yes/No/Unknown',
        }


class DataForm(forms.ModelForm):
    class Meta:
        model = models.Data
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),
            'species': forms.SelectMultiple(attr_chosen),
            'samples_collected': forms.SelectMultiple(multi_select_js),
            'sample_entered_database': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'samples_collected_database': forms.SelectMultiple(multi_select_js),
            'sample_barrier': forms.SelectMultiple(multi_select_js),
            'barrier_data_check_entry': forms.SelectMultiple(multi_select_js),
            'sample_format': forms.SelectMultiple(multi_select_js),
            'data_products': forms.SelectMultiple(multi_select_js),
            'data_products_database': forms.SelectMultiple(multi_select_js),
            'data_programs': forms.SelectMultiple(multi_select_js),
            'data_communication': forms.SelectMultiple(multi_select_js),
            'data_quality_check': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'samples_collected': 'Sample types <u>actually</u> collected for the project',
            'samples_collected_comment': 'Open Text',
            'samples_collected_database': 'Databases or shared drives where any raw, unanalyzed data is stored',
            'sample_barrier': 'What category of difficulties were encountered towards sample collection?',
            'sample_entered_database': 'Yes/No/Unknown',
            'data_quality_check': 'Yes/No/Unknown',
            'data_quality_person': 'Open Text',
            'barrier_data_check_entry': 'What category of difficulties were encountered towards data checks/enter into database?',
            'sample_format': 'Format of data that is received by DFO from First Nations',
            'data_products': 'Intermediate or final data product that can be produced from all or part sample collections',
            'data_products_database': 'Databases or shared drives where any partial or fully-analyzed data is stored',
            'data_products_comment': 'Open Text',
            'data_programs': 'Software used in the analysis of any data at any stage in the sample collection or data analysis process of the project',
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Feedback
        fields = '__all__'
        widgets = {
            'sent_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }


class MeetingsForm(forms.ModelForm):
    class Meta:
        model = models.Meetings
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }


class ReportsForm(forms.ModelForm):
    class Meta:
        model = models.Reports
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),
            'report_timeline': forms.Select(choices=choices.REPORT_TIMELINE, attrs=attr_chosen),
            'report_type': forms.Select(choices=choices.REPORT_TYPE, attrs=attr_chosen),
            'published': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts ={
            'report_timeline': 'Identifies whether a report was prepared during or following completion of the project',
            'report_type': 'A general category of what type of reports are associated as an outcome of the project',
            'report_concerns': 'Open Text',
            'document_name': 'Report Document Title',
            'document_author': 'Author Document',
            'document_reference_information': 'Report document reference number/catalogue number',
            'document_link': 'Report Document Link',
        }


class SampleOutcomeForm(forms.ModelForm):

    class Meta:
        model = models.SampleOutcome
        fields = '__all__'
        widgets = {
            'objective': forms.HiddenInput(),
            'location': forms.SelectMultiple(attr_chosen),
            'species': forms.Select(attr_chosen),
            'sampling_outcome': forms.Select(choices=choices.SAMPLE_TYPE_OUTCOMES, attrs=attr_chosen),
            'outcome_quality': forms.Select(choices=choices.DATA_QUALITY, attrs=attr_chosen),
            'outcome_delivered': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'outcome_report_delivered': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'unique_objective_number': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'sampling_outcome': 'Specific sampling outcomes expected for the project',
            'outcome_quality': 'General scale of quality of reports, data collection and project operations',
            'outcome_delivered': 'Yes/No/Unknown'
        }


class ReportOutcomeForm(forms.ModelForm):
    class Meta:
        model = models.ReportOutcome
        fields = '__all__'
        widgets = {
            'objective': forms.HiddenInput(),
            'reporting_outcome': forms.Select(choices=choices.OUTCOMES, attrs=attr_chosen),
            'outcome_delivered': forms.Select(choices=choices.YES_NO_UNKNOWN, attrs=attr_chosen),
            'unique_objective_number': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'reporting_outcome': 'What form are the intended scientific outcomes going to be delivered in?',
            'outcome_delivered': 'Yes/No/Unknown',
            'report_link': 'Report that inlcudes information relating to project objectives being met/delivered',
        }


class RiverForm(forms.ModelForm):
    class Meta:
        model = models.River
        fields = '__all__'


class WatershedForm(forms.ModelForm):
    class Meta:
        model = models.River
        fields = '__all__'


class LakeSystemForm(forms.ModelForm):
    class Meta:
        model = models.River
        fields = '__all__'


class FundingYearForm(forms.ModelForm):
    class Meta:
        model = models.FundingYears
        fields = '__all__'

        widgets = {
            'project': forms.HiddenInput(),
            'funding_year': forms.Select(choices=choices.FUNDING_YEARS, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'funding_year': 'Years in which the project is in operation',
            'agreement_cost': 'Monetary value of the total agreement',
            'project_cost': 'Monetary value of the specific activity being described',

        }


class MethodDocumentForm(forms.ModelForm):
    class Meta:
        model = models.MethodDocument
        fields = '__all__'

        widgets = {
            'method': forms.HiddenInput(),
            'method_document_type':forms.Select(choices=choices.METHOD_DOCUMENT, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'method_document_type': 'General categorization of any protocol that is being followed for the project',
            'authors': 'Author of method document',
            'publication_year': 'Year of method document development',
            'title': 'Title of method document',
            'reference_number': 'Reference number, if applicable, of method document',
            'document_link': 'Link to method document',
        }


class ProjectCertifiedForm(forms.ModelForm):
    class Meta:
        model = models.ProjectCertified
        fields = '__all__'

        widgets = {
            'project': forms.HiddenInput(),
            'certified': forms.Select(choices=YES_NO_CHOICES, attrs=attr_chosen)
        }


class SpotUserForm(forms.ModelForm):
    class Meta:
        model = models.SpotUser
        fields = "__all__"
        widgets = {
            'user': forms.Select(attrs=attr_chosen_contains),
        }


SpotUserFormset = modelformset_factory(
    model=models.SpotUser,
    form=SpotUserForm,
    extra=1,
)
