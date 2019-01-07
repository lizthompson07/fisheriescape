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
    SITE_CHOICES = ((None, "---"),)
    for obj in models.Site.objects.all().order_by("site"):
        SITE_CHOICES = SITE_CHOICES.__add__(((obj.id, obj),))

    STATION_CHOICES = ((None, "---"),)
    for obj in models.Station.objects.all():
        STATION_CHOICES = STATION_CHOICES.__add__(((obj.id, obj),))

    SPECIES_CHOICES = ((None, "---"),)
    for obj in models.Species.objects.all():
        SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))

    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': "all years"}))
    month = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': "all months"}))
    site = forms.ChoiceField(required=False, choices=SITE_CHOICES)
    station = forms.ChoiceField(required=False, choices=STATION_CHOICES)
    species = forms.ChoiceField(required=False, choices=SPECIES_CHOICES)

    field_order = ["year", "month", "site", "station", "species"]


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
    SPECIES_CHOICES = ((None, "---"),)
    for obj in models.Species.objects.all().order_by("common_name_eng"):
        SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))

    SITE_CHOICES = ((None, "All Stations"),)
    for obj in models.Site.objects.all():
        SITE_CHOICES = SITE_CHOICES.__add__(((obj.id, obj),))

    REPORT_CHOICES = (
        (None, "---"),
        (1, "Species counts by year"),
        (2, "Species richness by year"),
        (3, "Annual watershed report (PDF)"),
        (4, "Annual watershed spreadsheet (XLSX)"),
        (5, "Dataset export for FGP (CSV)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    species = forms.MultipleChoiceField(required=False, choices=SPECIES_CHOICES)
    year = forms.CharField(required=False, widget=forms.NumberInput())
    site = forms.ChoiceField(required=False, choices=SITE_CHOICES)
