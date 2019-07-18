from django import forms
from django.core import validators
from shared_models import models as shared_models

from . import models

attr_fp_date_time = {"class": "fp-date-time", "placeholder": "Select Date and Time.."}
attr_fp_date = {"class": "fp-date", "placeholder": "Select Date.."}
multi_select_js = {"class": "multi-select"}
chosen_js = {"class": "chosen-select-contains"}


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"


class RiverForm(forms.ModelForm):
    class Meta:
        model = shared_models.River
        fields = "__all__"


class RiverSiteForm(forms.ModelForm):
    class Meta:
        model = models.RiverSite
        fields = "__all__"
        widgets = {
            "latitude_n": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "longitude_w": forms.NumberInput(attrs={"placeholder": "DD.dddddd", }),
            "directions": forms.Textarea(attrs={"rows": "3", }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("instance") or kwargs.get("initial"):
            self.fields["river"].widget = forms.HiddenInput()


class SampleForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        exclude = ["last_modified", 'season']
        widgets = {
            "site": forms.HiddenInput(),
            "last_modified_by": forms.HiddenInput(),
            "samplers": forms.Textarea(attrs={"rows": "2", }),
            "notes": forms.Textarea(attrs={"rows": "3", }),
            "arrival_date": forms.DateTimeInput(attrs=attr_fp_date_time),
            "departure_date": forms.DateTimeInput(attrs=attr_fp_date_time),
        }

class EntryForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        fields = "__all__"
        widgets = {
            'species': forms.HiddenInput(),
            'sample': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": "3"}),
            "date_tagged": forms.DateTimeInput(attrs=attr_fp_date),
        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "---"),
        (1, "List of samples (trap data) (.CSV)"),
        (2, "List of entries (fish data) (.CSV)"),
        (3, "OPEN DATA - summary by site by year (.CSV)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    year = forms.CharField(required=False, widget=forms.NumberInput(), label="Year (optional)")

    # species = forms.MultipleChoiceField(required=False)
    # ais_species = forms.MultipleChoiceField(required=False, label="AIS species")
    # site = forms.ChoiceField(required=False)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     SITE_CHOICES = [(obj.id, str(obj)) for obj in models.Site.objects.all()]
    #     SITE_CHOICES.insert(0, tuple((None, "All Sites")))
    #
    #     SPECIES_CHOICES = [(obj.id, str(obj)) for obj in models.Species.objects.all().order_by("common_name_eng")]
    #     SPECIES_CHOICES.insert(0, tuple((None, "-------")))
    #
    #     AIS_CHOICES = [(obj.id, "{} - {}".format(obj.common_name_eng, obj.scientific_name)) for obj in
    #                    models.Species.objects.filter(ais=True).order_by("common_name_eng")]
    #
    #     self.fields['site'].choices = SITE_CHOICES
    #     self.fields['species'].choices = SPECIES_CHOICES
    #     self.fields['ais_species'].choices = AIS_CHOICES

        # SPECIES_CHOICES = ((None, "---"),)
        # for obj in models.Species.objects.all().order_by("common_name_eng"):
        #     SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))
        #
        # SITE_CHOICES = ((None, "All Stations"),)
        # for obj in models.Site.objects.all():
        #     SITE_CHOICES = SITE_CHOICES.__add__(((obj.id, obj),))
