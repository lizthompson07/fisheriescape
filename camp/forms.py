from django import forms
from django.core import validators

from . import models


class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        fields = "__all__"


class StationForm(forms.ModelForm):
    class Meta:
        model = models.Station
        fields = "__all__"
        widgets = {
            "latitude_n": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "longitude_w": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "description": forms.Textarea(attrs={"rows": "3", }),
            "site": forms.HiddenInput(),
        }


class NoSiteStationForm(forms.ModelForm):
    class Meta:
        model = models.Station
        fields = "__all__"
        widgets = {
            "latitude_n": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "longitude_w": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "description": forms.Textarea(attrs={"rows": "3", }),
            # "site": forms.HiddenInput(),
        }


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"


class SearchForm(forms.Form):

    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': "all years"}))
    month = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': "all months"}))

    field_order = ["year", "month", "site", "station", "species"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        site_choices = [(obj.id, str(obj)) for obj in models.Site.objects.all()]
        site_choices.insert(0, tuple((None, "---")))

        station_choices = [(obj.id, str(obj)) for obj in models.Station.objects.all()]
        station_choices.insert(0, tuple((None, "---")))

        species_choices = [(obj.id, str(obj)) for obj in models.Species.objects.all()]
        species_choices.insert(0, tuple((None, "---")))

        self.fields['site'] = forms.ChoiceField(required=False, choices=site_choices)
        self.fields['station'] = forms.ChoiceField(required=False, choices=station_choices)
        self.fields['species'] = forms.ChoiceField(required=False, choices=species_choices)


class SampleForm(forms.ModelForm):
    do_another = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.Sample
        exclude = [
            'species',
            'sample_spp',
            'year',
            'month',
            'last_modified',
        ]
        labels = {
            'notes': "Misc. notes",
        }

        class_addable = {"class": "addable"}

        widgets = {
            'notes': forms.Textarea(attrs={'rows': '3'}),
            'percent_sand': forms.NumberInput(attrs=class_addable),
            'percent_gravel': forms.NumberInput(attrs=class_addable),
            'percent_rock': forms.NumberInput(attrs=class_addable),
            'percent_mud': forms.NumberInput(attrs=class_addable),
        }


class SampleCreateForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        exclude = [
            'species',
            'sample_spp',
            'year',
            'month',
            'last_modified',
        ]
        labels = {
            'notes': "Misc. notes",
        }

        class_addable = {"class": "addable"}

        widgets = {
            'notes': forms.Textarea(attrs={'rows': '3'}),
            'percent_sand': forms.NumberInput(attrs=class_addable),
            'percent_gravel': forms.NumberInput(attrs=class_addable),
            'percent_rock': forms.NumberInput(attrs=class_addable),
            'percent_mud': forms.NumberInput(attrs=class_addable),
        }


class NonSAVObservationForm(forms.ModelForm):
    class Meta:
        model = models.SpeciesObservation
        exclude = [
            'total_sav',
            'total_non_sav',
        ]
        labels = {

        }
        widgets = {
            'species': forms.HiddenInput(),
            'sample': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": "3"}),
        }


class SAVObservationForm(forms.ModelForm):
    class Meta:
        model = models.SpeciesObservation
        exclude = [
            'total_non_sav',
            'adults',
            'yoy',
        ]
        labels = {

        }
        widgets = {
            'species': forms.HiddenInput(),
            'sample': forms.HiddenInput(),
            # 'percent_coverage':forms.TextInput(attrs={'placeholder':"Value bewteen 0 and 1"}),
            'notes': forms.Textarea(attrs={"rows": "3"}),

        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "---"),
        (1, "Species counts by year"),
        (3, "Annual watershed report (PDF)"),
        (4, "Annual watershed spreadsheet (XLSX)"),
        (6, "AIS export (CSV)"),
        (5, "OPEN DATA: export for FGP (CSV)"),
        (7, "OPEN DATA: data dictionary for FGP (CSV)"),
        (8, "OPEN DATA: web mapping services report (CSV)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    species = forms.MultipleChoiceField(required=False)
    ais_species = forms.MultipleChoiceField(required=False, label="AIS species")
    year = forms.CharField(required=False, widget=forms.NumberInput())
    site = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        SITE_CHOICES = [(obj.id, str(obj)) for obj in models.Site.objects.all()]
        SITE_CHOICES.insert(0, tuple((None, "All Sites")))

        SPECIES_CHOICES = [(obj.id, str(obj)) for obj in models.Species.objects.all().order_by("common_name_eng")]
        SPECIES_CHOICES.insert(0, tuple((None, "-------")))

        AIS_CHOICES = [(obj.id, "{} - {}".format(obj.common_name_eng, obj.scientific_name)) for obj in
                       models.Species.objects.filter(ais=True).order_by("common_name_eng")]

        self.fields['site'].choices = SITE_CHOICES
        self.fields['species'].choices = SPECIES_CHOICES
        self.fields['ais_species'].choices = AIS_CHOICES

        # SPECIES_CHOICES = ((None, "---"),)
        # for obj in models.Species.objects.all().order_by("common_name_eng"):
        #     SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))
        #
        # SITE_CHOICES = ((None, "All Stations"),)
        # for obj in models.Site.objects.all():
        #     SITE_CHOICES = SITE_CHOICES.__add__(((obj.id, obj),))
