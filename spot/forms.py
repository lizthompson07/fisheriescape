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
            'province': forms.Select(choices=choices.PROVINCE_STATE_CHOICES, attrs=attr_chosen),
            'country': forms.Select(choices=choices.COUNTRY_CHOICES, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
        }


class PersonForm(forms.ModelForm):

    organizations = forms.ModelMultipleChoiceField(queryset=models.Organization.objects.all(), widget=forms.SelectMultiple(attrs=multi_select_js))

    class Meta:
        model = models.Person
        fields = '__all__'
        widgets = {
            'province': forms.Select(choices=choices.PROVINCE_STATE_CHOICES, attrs=attr_chosen),
            'role': forms.Select(choices=choices.ROLE, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }


class ProjectForm(forms.ModelForm):

    class Meta:
        model = models.Project
        fields = '__all__'
        widgets = {
            'ecosystem_type': forms.Select(choices=choices.ECOSYSTEM_TYPE, attrs=attr_chosen),
            'region': forms.Select(choices=choices.REGION, attrs=attr_chosen),
            'species': forms.SelectMultiple(choices=choices.SPECIES, attrs=multi_select_js),
            'smu_name': forms.Select(choices=choices.SMU_NAME, attrs=attr_chosen),
            'salmon_life_stage': forms.SelectMultiple(choices=choices.SALMON_LIFE_CYCLE, attrs=multi_select_js),
            'project_stage': forms.Select(choices=choices.PROJECT_STAGE,attrs=attr_chosen),
            'project_type': forms.Select(choices=choices.PROJECT_TYPE, attrs=attr_chosen),
            'project_sub_type': forms.SelectMultiple(choices=choices.PROJECT_SUB_TYPE, attrs=multi_select_js),
            'monitoring_approach': forms.Select(choices=choices.MONITORING_APPROACH, attrs=attr_chosen),
            'project_theme': forms.SelectMultiple(choices=choices.PROJECT_THEME, attrs=multi_select_js),
            'core_component': forms.SelectMultiple(choices=choices.PROJECT_CORE_ELEMENT, attrs=multi_select_js),
            'supportive_component': forms.SelectMultiple(choices=choices.SUPPORTIVE_COMPONENT, attrs=multi_select_js),
            'project_purpose': forms.SelectMultiple(choices=choices.PROJECT_PURPOSE, attrs=multi_select_js),
            'DFO_link': forms.Select(choices=choices.DFO_LINK, attrs=attr_chosen),
            'government_organization': forms.Select(choices=choices.GOVERNMENT_LINK, attrs=attr_chosen),
            'primary_first_nations_contact_role': forms.Select(choices=choices.ROLE, attrs=attr_chosen),
            'start_date': forms.SelectDateWidget(years=range(1950, 2050)),
            'end_date': forms.SelectDateWidget(years=range(1950, 2050)),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        labels = {
            'management_area': mark_safe('Management area:<a href="https://www.pac.dfo-mpo.gc.ca/fm-gp/maps-cartes/areas-secteurs/index-eng.html" target="_blank"> Map of Area 1-142</a> '),
        }


class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = models.Objective
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),
            'activity': forms.Select(choices=choices.ACTIVITY_NUMBER, attrs=attr_chosen),
            'key_element': forms.Select(choices=choices.KEY_ELEMENT, attrs=attr_chosen),
            'element_title': forms.Select(choices=choices.ELEMENT_TITLE, attrs=attr_chosen),
            'species': forms.SelectMultiple(choices=choices.SPECIES, attrs=multi_select_js),
            'objective_category': forms.SelectMultiple(choices=choices.PROJECT_THEME, attrs=multi_select_js),
            'outcome_barrier': forms.SelectMultiple(choices=choices.OUTCOME_BARRIER, attrs=multi_select_js),
            'capacity_building': forms.SelectMultiple(choices=choices.CAPACITY, attrs=multi_select_js),
            'outcome_deadline': forms.DateInput(),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }


class MethodForm(forms.ModelForm):
    class Meta:
        model = models.Method
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),
            'planning_method_type': forms.SelectMultiple(choices=choices.PLANNING_METHOD, attrs=multi_select_js),
            'field_work_method_type': forms.SelectMultiple(choices=choices.FIELD_WORK, attrs=multi_select_js),
            'sample_processing_method_type': forms.SelectMultiple(choices=choices.SAMPLE_PROCESSING, attrs=multi_select_js),
            'data_entry_method_type': forms.SelectMultiple(choices=choices.DATA_ENTRY, attrs=multi_select_js),
            'method_document_type': forms.Select(choices=choices.METHOD_DOCUMENT, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            ''
        }


class DataForm(forms.ModelForm):
    class Meta:
        model = models.Data
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),
            'species_data': forms.SelectMultiple(choices=choices.SPECIES, attrs=multi_select_js),
            'samples_collected': forms.SelectMultiple(choices=choices.SAMPLES_COLLECTED, attrs=multi_select_js),
            'samples_collected_database': forms.SelectMultiple(choices=choices.DATABASE, attrs=multi_select_js),
            'sample_barrier': forms.SelectMultiple(choices=choices.SAMPLE_BARRIER, attrs=multi_select_js),
            'barrier_data_check_entry': forms.SelectMultiple(choices=choices.DATA_BARRIER, attrs=multi_select_js),
            'sample_format': forms.SelectMultiple(choices=choices.SAMPLE_FORMAT, attrs=multi_select_js),
            'data_products': forms.SelectMultiple(choices=choices.DATA_PRODUCTS, attrs=multi_select_js),
            'data_products_database': forms.SelectMultiple(choices=choices.DATABASE, attrs=multi_select_js),
            'data_programs': forms.SelectMultiple(choices=choices.DATA_PROGRAMS, attrs=multi_select_js),
            'data_communication': forms.SelectMultiple(choices=choices.DATA_COMMUNICATION, attrs=multi_select_js),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
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

    def __init__(self, *args, **kwargs):
        super(MeetingsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


class ReportsForm(forms.ModelForm):
    class Meta:
        model = models.Reports
        fields = '__all__'
        widgets = {
            'project': forms.HiddenInput(),
            'report_timeline': forms.Select(choices=choices.REPORT_TIMELINE, attrs=attr_chosen),
            'report_type': forms.Select(choices=choices.REPORT_TYPE, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }


class ObjectiveDataTypeQualityForm(forms.ModelForm):
    class Meta:
        model = models.ObjectiveDataTypeQuality
        fields = '__all__'
        widgets = {
            'objective': forms.HiddenInput(),
            'sample_type': forms.Select(choices=choices.SAMPLE_TYPE_OUTCOMES, attrs=attr_chosen),
            'outcome_quality': forms.Select(choices=choices.DATA_QUALITY, attrs=attr_chosen),
            'report_sent': forms.Select(choices=choices.REPORT_SENT, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }


class ObjectiveOutcomeForm(forms.ModelForm):
    class Meta:
        model = models.ObjectiveOutcome
        fields = '__all__'
        widgets = {
            'objective': forms.HiddenInput(),
            'outcome_category': forms.Select(choices=choices.OUTCOMES, attrs=attr_chosen),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
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
        'sample_type': forms.Select(choices=choices.FUNDING_YEARS, attrs=attr_chosen),
        'last_modified_by': forms.HiddenInput(),
        'date_last_modified': forms.HiddenInput(),
    }


class MethodDocumentForm(forms.ModelForm):
    class Meta:
        model = models.MethodDocument
        fields = '__all__'

    widgets = {
        'method': forms.HiddenInput(),
        'last_modified_by': forms.HiddenInput(),
        'date_last_modified': forms.HiddenInput(),
    }