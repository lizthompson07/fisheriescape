from django import forms
from django.contrib.auth.models import User
from django.core import validators
from . import models

attr_fp_date_time = {"class": "fp-date-time", "placeholder": "Select Date and Time.."}
multi_select_js = {"class": "multi-select"}


class StationForm(forms.ModelForm):
    class Meta:
        model = models.Station
        fields = "__all__"
        labels = {
            'site_desc': "Site description",
            'depth': "Depth (m)",
        }
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class EstuaryForm(forms.ModelForm):
    class Meta:
        model = models.Estuary
        fields = "__all__"
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        fields = "__all__"
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'estuary': forms.HiddenInput(),
        }


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class GCSampleForm(forms.ModelForm):
    class Meta:
        model = models.GCSample
        exclude = ['last_modified', 'season']
        widgets = {
            'traps_set': forms.DateTimeInput(attrs=attr_fp_date_time),
            'traps_fished': forms.DateTimeInput(attrs=attr_fp_date_time),
            'last_modified_by': forms.HiddenInput(),
            'samplers': forms.SelectMultiple(attrs=multi_select_js),
            'vegetation_species': forms.SelectMultiple(attrs=multi_select_js),
        }


class SampleForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        exclude = ['date_created', 'last_modified', 'season', 'notes_html', 'days_deployed', 'collector_lines',
                   'species', 'old_substn_id']
        labels = {
            'site_desc': "Site description",
            'samplers': "Samplers"
        }
        widgets = {
            'date_deployed': forms.DateInput(attrs={'type': 'date'}),
            'date_retrieved': forms.DateInput(attrs={'type': 'date'}),
            'last_modified_by': forms.HiddenInput(),

        }


class SampleNoteForm(forms.ModelForm):
    class Meta:
        model = models.SampleNote
        fields = "__all__"
        widgets = {
            'author': forms.HiddenInput(),
            'sample': forms.HiddenInput(),

        }


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = models.FollowUp
        fields = "__all__"
        widgets = {
            'incidental_report': forms.HiddenInput(),
            'note': forms.Textarea(attrs={"rows": 6}),
            'date': forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        User.objects.all().order_by("last_name", "first_name")]
        USER_CHOICES.insert(0, tuple((None, "---")))

        self.fields['author'].queryset = User.objects.all().order_by("last_name", "first_name")
        self.fields['author'].choices = USER_CHOICES


class ProbeMeasurementForm(forms.ModelForm):
    class Meta:
        fields = ("__all__")
        model = models.ProbeMeasurement

        widgets = {
            'time_date':forms.DateTimeInput(attrs=attr_fp_date_time),
            'last_modified_by': forms.HiddenInput(),
            'sample': forms.HiddenInput(),

        }


class GCProbeMeasurementForm(forms.ModelForm):
    class Meta:
        fields = ("__all__")
        model = models.GCProbeMeasurement
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'sample': forms.HiddenInput(),
        }


class LineCreateForm(forms.ModelForm):
    number_plates = forms.IntegerField(label='How many plates on this line?', required=False)
    number_petris = forms.IntegerField(label='How many petri dishes on this line?', required=False)

    class Meta:
        model = models.Line
        exclude = ["species", ]
        labels = {
            'collector': "DFO collector tag #",
            'latitude_n': "Latitude (N) e.g., 46.0123",
            'longitude_w': "Longitude (W) e.g., -64.0789",
        }
        widgets = {
            'latitude_n': forms.NumberInput(attrs={'placeholder': 'decimal degrees'}),
            'longitude_w': forms.NumberInput(attrs={'placeholder': 'decimal degrees'}),
            'notes': forms.Textarea(attrs={'rows': '5'}),
            'last_modified_by': forms.HiddenInput(),
            'sample': forms.HiddenInput(),
        }


class LineForm(forms.ModelForm):
    class Meta:
        model = models.Line
        exclude = ['species', ]
        labels = {
            'collector': "DFO collector tag #",
            'latitude_n': "Latitude (N)",
            'longitude_w': "Longitude (W)",
        }
        widgets = {
            'latitude_n': forms.NumberInput(attrs={'placeholder': 'decimal degrees'}),
            'longitude_w': forms.NumberInput(attrs={'placeholder': 'decimal degrees'}),
            'notes': forms.Textarea(attrs={'rows': '5'}),
            'last_modified_by': forms.HiddenInput(),
            'sample': forms.HiddenInput(),
        }


class SurfaceForm(forms.ModelForm):
    class Meta:
        model = models.Surface
        fields = "__all__"
        exclude = ['species']
        widgets = {
            'line': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
        }


class SurfaceImageForm(forms.ModelForm):
    class Meta:
        model = models.Surface
        fields = ('image', 'last_modified_by')
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class SurfaceSpeciesForm(forms.ModelForm):
    class Meta:
        model = models.SurfaceSpecies
        fields = "__all__"
        labels = {
            'percent_coverage': "Coverage",
            'notes': "Optional notes",
        }
        widgets = {
            'species': forms.HiddenInput(),
            'surface': forms.HiddenInput(),
            'percent_coverage': forms.TextInput(attrs={'placeholder': "Value bewteen 0 and 1"}),
            'notes': forms.Textarea(attrs={"rows": "3", "placeholder": ""}),
            'last_modified_by': forms.HiddenInput(),
        }


class SampleSpeciesForm(forms.ModelForm):
    class Meta:
        model = models.SampleSpecies
        fields = "__all__"
        labels = {
            # 'percent_coverage':"Coverage",
            # 'notes':"Optional notes",
        }
        widgets = {
            'species': forms.HiddenInput(),
            'sample': forms.HiddenInput(),
            'observation_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={"rows": "3", "placeholder": ""}),
        }


class LineSpeciesForm(SampleSpeciesForm):
    class Meta:
        model = models.LineSpecies
        fields = "__all__"
        labels = {
            # 'percent_coverage':"Coverage",
            # 'notes':"Optional notes",
        }
        widgets = {
            'species': forms.HiddenInput(),
            'line': forms.HiddenInput(),
            'observation_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={"rows": "3", "placeholder": ""}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = models.IncidentalReport
        exclude = ["season", "date_last_modified", "species"]

        labels = {
            'reporter_name': "Name of person filing report",
            'notes': "Notes (e.g., habitat, salinity, temperature, etc...) ",
            'report_date': "Date report received",
        }

        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_occurrence': forms.DateInput(attrs={'type': 'date'}),
            'sighting_description': forms.Textarea(attrs={'rows': '3'}),
            'notes': forms.Textarea(attrs={'rows': '3'}),
            'last_modified_by': forms.HiddenInput(),
            # 'species':forms.SelectMultiple(attr={"name":"id_species[]"})
        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, ""),
        (None, "----- BIOFOULING ------"),
        (1, "Biofouling: Species observations by sample"),
        (None, ""),
        (None, "----- GREEN CRAB ------"),
        (8, "Green Crab: Site descriptions (xlsx)"),
        (6, "Green Crab: Fukui traps/CPUE data (xlsx)"),
        (7, "Green Crab: Environmental data (xlsx)"),
        (None, ""),
        (None, "----- OPEN DATA ------"),
        (3, "OPEN DATA: Data dictionary (csv)"),
        (4, "OPEN DATA: WMS report ENGLISH (csv)"),
        (5, "OPEN DATA: WMS report FRENCH (csv)"),
        (2, "OPEN DATA - Version 1: Biofouling monitoring program"),

    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    species = forms.MultipleChoiceField(required=False)
    year = forms.CharField(required=False, widget=forms.NumberInput(), label="Year")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        species_choices = [(obj.id, "{} ({})".format(obj.scientific_name, obj.common_name)) for obj in
                           models.Species.objects.all().order_by("scientific_name")]

        self.fields['species'].choices = species_choices


class TrapForm(forms.ModelForm):
    class Meta:
        model = models.Trap
        fields = "__all__"
        widgets = {
            'latitude_n': forms.NumberInput(attrs={'placeholder': 'decimal degrees'}),
            'longitude_w': forms.NumberInput(attrs={'placeholder': 'decimal degrees'}),
            'notes': forms.Textarea(attrs={'rows': '5'}),
            'last_modified_by': forms.HiddenInput(),
            'sample': forms.HiddenInput(),
        }


class CrabForm(forms.ModelForm):
    class Meta:
        model = models.Crab
        fields = "__all__"
        widgets = {
            'species': forms.HiddenInput(),
            'trap': forms.HiddenInput(),
            # 'percent_coverage': forms.TextInput(attrs={'placeholder': "Value bewteen 0 and 1"}),
            'notes': forms.Textarea(attrs={"rows": "3", "placeholder": ""}),
            'last_modified_by': forms.HiddenInput(),
        }


class BycatchForm(forms.ModelForm):
    class Meta:
        model = models.Bycatch
        fields = "__all__"
        widgets = {
            'species': forms.HiddenInput(),
            'trap': forms.HiddenInput(),
            # 'percent_coverage': forms.TextInput(attrs={'placeholder': "Value bewteen 0 and 1"}),
            'notes': forms.Textarea(attrs={"rows": "3", "placeholder": ""}),
            'last_modified_by': forms.HiddenInput(),
        }
