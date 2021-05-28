from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from . import models
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminDateWidget

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
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'organization_type': 'its a mighty <br> cheese pizza',
            'address': 'where ya live'
        }

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


class PersonForm(forms.ModelForm):

    #organizations = forms.ModelMultipleChoiceField(queryset=models.Organization.objects.all(), widget=forms.SelectMultiple(attrs=attr_chosen_contains))

    class Meta:
        model = models.Person #ml
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


class ProjectForm(forms.ModelForm):

    #government_organizations = forms.ModelMultipleChoiceField(queryset=models.Organization.objects.all(), widget=forms.SelectMultiple(attrs=attr_chosen_contains))

    class Meta:
        model = models.Project
        fields = '__all__'
        widgets = {
            'start_date': forms.SelectDateWidget(years=range(1950, 2050)),
            'end_date': forms.SelectDateWidget(years=range(1950, 2050)),
            'last_modified_by': forms.HiddenInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_last_modified': forms.HiddenInput(),
        }
        labels = {
            'management_area': mark_safe('Management area:<a href="https://www.pac.dfo-mpo.gc.ca/fm-gp/maps-cartes/areas-secteurs/index-eng.html" target="_blank"> Map of Area 1-142</a> '),
        }
        help_texts = {
            'agreement_number': 'Most current and primary agreement number',
            'agreement_database': 'Primary or originating database where the primary agreement documentation is held',
            'agreement_status': '<b>Complete</b> - Agreement objectives have been met with no active work ongoing <br>'
                                '<b>Continuing</b> - Work is ongoing that is outlined in the agreement<br>'
                                '<b>Inactive</b> - Project objectives are incomplete and work is not ongoing<br>'
                                '<b>Unknown</b> - For unknown reasons, certified agreement project is not being carried out',
            'funding_years': 'Select all years that apply',
            'management_area': 'Select from areas 1-142',
            'region': 'DFO Management regions',
            'primary_river': 'Main river where field work/assessment or data is being collected on',
            'smu_name': 'Stock Management Unit',
            'species': 'Salmon species, do not leave blank',
            'salmon_life_cycle': '<b>Adult</b> - Adult salmon typically residing in the ocean, feeding on smaller fish and maturing<br>'
                                 '<b>Juvenile</b> - Fish in the fry, parr, & smolt stage of life<br>'
                                 '<b>Parr</b> - Older juveniles with prominent parr marks (darker vertical lines)<br>'
                                 '<b>Smolt</b> - Typically reside in the lower reaches of the river/estuary where they are physiologically ready to go to sea<br>'
                                 '<b>Fry</b> - Salmon have absorbed their yolk sacs and emerged from the gravel ready to feed<br>'
                                 '<b>Spawning</b> - A phase of the salmonid life cycle where male and female fish are in the spawning grounds, are mature and able to spawn<br>'
                                 '<b>Egg & Alevin</b> - Salmon eggs and newly hatched young with an unabsorbed yolk sac',
            'project_stage': '<b>Developing</b> - The process of planning, organizing, coordinating, and controlling the resources to accomplish specific goals<br>'
                             '<b>Pilot</b> - A "small"  study to test research protocols, data collection, instruments, sample recruitment strategies and other research techniques in preparation for a larger study<br>'
                             '<b>Operational</b> - The on-going physical activities (eg data collection, analysis) related to the objectives or deliverables of a project<br>'
                             '<b>Complete</b> - No further activities are being conducted<br>'
                             '<b>Terminated</b> - Project has been halted with no plans to restart<br>'
                             '<b>Merged</b> - Project has been combined with another',
            'project_scale': '<b>Large</b> – Several groups contributing to data collection; project has been ongoing for >5 years; or many resources are devoted to the operation of the project.<br>' 
                             '<b>Medium</b> – One or two groups contributing to data collection; project has been ongoing for <5 years; or a typical amount of resources are devoted to the operation of the project.<br>' 
                             '<b>Small</b> – One group is contributing to data collection; project is only for a year or two; or few resources are devoted to the operation of the project.',
            'project_type': '<b>Population Science</b> – monitoring of a biological characteristic of a fish stock including catch.<br>'
                            '<b>Habitat Science</b> – the monitoring of a physical or chemical aspect of habitat or environment',
            'project_sub_type': '<b>Research & Development</b> – testing or experimenting different conditions for a fish population or habitat<br>'
                                '<b>Monitoring</b> - catch-all term for projects relating to data collected for fish enumeration or measuring habitat parameters.<br>'
                                '<b>Sampling</b> – catch-all term for projects relating to data collected for further laboratory analysis (age, genetics, plankton identification etc.) of fish or habitat parameters.<br>'
                                '<b>Recovery</b> – improvements, enhancements being made to fish or fish habitat in an effort to increase production/productivity.<br>',
            'monitoring_approach': '<b>Indicator</b> – a stock that has been identified as an indicator stock whereby the fish from these locations or populations (can include enhancement) are assumed to be representative of some aspect of a Conservation Unit (CU).<br>'
                                   '<b>Intensive</b> – sites where more accurate and precise estimates of escapement, catch, and stock-recruitment are obtained. Information collected from intensively monitored sites may also include data on returning adult salmon (age, sex, DNA, etc.), and on fry and juvenile fish.<br>'
                                   '<b>Extensive</b> – sites where escapements are monitored at a coarser level with lower precision and accuracy, but over a much broader geographic area.<br>',
            'project_theme': '<b>Escapement</b> – data collected to estimate the number of mature salmon that pass through (or escape) fisheries and return to fresh water to spawn.<br>'
                             '<b>Conservation</b> – data collected to inform the protection, maintenance and rehabilitation of genetic diversity, species, and ecosystems/habitat to sustain biodiversity and the continuance of evolutionary and natural production processes.<br>'
                             '<b>Catch</b> – data collected during the act of removing fish from their populations by means of recreational, commercial or first nations fisheries.<br>'
                             '<b>Enhancement</b>– the application of biological, physical or technical knowledge and capabilities to increase the productivity of fish stocks.<br>'
                             '<b>Administration</b> – an immediate and administrative-focused project including data (no fish or habitat information collected).<br>',
            'core_component': '<b>Planning</b> – initial study, project design, resource allocation etc. or objective-setting to carry out a project.<br>' 
                              '<b>Field Work</b> – the immediate act of carrying out work (counts, tissue collection, habitat data etc.) that yields data related to the project’s objectives.<br>'
                              '<b>Sample Processing</b> – data collected in the field that requires further testing, alternation or study (aging, genetics etc.)<br>'
                              '<b>Data Entry</b> – the act of entering data information into a computer (individual or database).<br>'
                              '<b>Data Analysis/<b> – the act of using data to compile, modify or test to create a data products (new data variable, graphs, data series etc.).<br>'
                              '<b>Reporting</b> – a collection of data or information which is summarized.',
            'supportive_component': 'TO BE COMPLETED',
            'DFO_link': 'TO BE COMPLETED',
            'DFO_program_reference': 'Please list either by agreement number or another project reference number or project authority. Please be specific as to the type of reference number you are providing.',
            'government_reference': 'Please list the agency’s section or department name, primary contact and any reference number.',
            'strategic_agreement_link': 'Links to Strategic documents/agreements',
            'primary_first_nations_contact_role': 'Primary role within the organization',
            'FN_relationship_level': '<b>Excellent</b> – High level of communication and cooperation.<br>' 
                                     '<b>Good</b> - Good level of communication and cooperation.<br>'
                                     '<b>Moderate</b> - Moderate level of communication and cooperation.<br>'
                                     '<b>Poor</b> - Poor level of communication and cooperation.',
            'other_first_nations_contact_role': 'Primary role within the organization',

        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = models.Objective
        fields = '__all__'
        widgets = {
            'outcomes_deadline': forms.DateInput(attrs={"type": "date"}),
            'pst_req': forms.Select(choices=YES_NO_CHOICES),
            'sil_req': forms.Select(choices=YES_NO_CHOICES),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ObjectiveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


class MethodForm(forms.ModelForm):
    class Meta:
        model = models.Method
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            ''
        }

    def __init__(self, *args, **kwargs):
        super(MethodForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


class DataForm(forms.ModelForm):
    class Meta:
        model = models.Data
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(DataForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Feedback
        fields = '__all__'
        widgets = {
            'sent_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


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
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ReportsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})
