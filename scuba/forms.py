from django import forms
from django.forms import modelformset_factory
from django.template.defaultfilters import date
from django.utils.translation import gettext, gettext_lazy

from . import models

attr_fp_date_time = {"class": "fp-date-time-with-seconds", "placeholder": "Select Date and Time.."}
chosen_js = {"class": "chosen-select-contains"}
YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class DiverForm(forms.ModelForm):
    class Meta:
        model = models.Diver
        fields = "__all__"


DiverFormset = modelformset_factory(
    model=models.Diver,
    form=DiverForm,
    extra=1,
)


class RegionForm(forms.ModelForm):
    class Meta:
        model = models.Region
        fields = "__all__"


class SiteForm(forms.ModelForm):
    field_order = ["name"]

    class Meta:
        model = models.Site
        fields = "__all__"


class TransectForm(forms.ModelForm):
    field_order = ["name"]

    class Meta:
        model = models.Transect
        fields = "__all__"


class SampleForm(forms.ModelForm):
    class Meta:
        model = models.Sample
        fields = "__all__"
        widgets = {
            "datetime": forms.DateInput(attrs=dict(type="date")),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        site_choices = [(site.id, f"{site.region} - {site}") for site in models.Site.objects.order_by("region", "name")]
        site_choices.insert(0, (None, "---------"))

        self.fields["site"].choices = site_choices


class DiveForm(forms.ModelForm):
    # field_order = ["name"]
    class Meta:
        model = models.Dive
        fields = "__all__"
        widgets = {
            "start_descent": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M:%S"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("instance"):
            self.fields["transect"].queryset = kwargs.get("instance").sample.site.transects.all()
        elif kwargs.get("initial"):
            self.fields["transect"].queryset = models.Sample.objects.get(pk=kwargs.get("initial").get("sample")).site.transects.all()

        # self.fields["start_descent"].label += " (yyyy-mm-dd HH:MM:SS)"

    def clean(self):
        if hasattr(self.instance, "sample"):
            sample = self.instance.sample
        else:
            sample = models.Sample.objects.get(pk=self.initial.get("sample"))

        cleaned_data = super().clean()

        start_descent = cleaned_data.get("start_descent")

        if start_descent and (start_descent.year != sample.datetime.year or
                              start_descent.month != sample.datetime.month or
                              start_descent.day != sample.datetime.day):
            msg = gettext(gettext('This must occur on the same day as the sample: {}').format(date(sample.datetime)))
            self.add_error('start_descent', msg)

        transect = cleaned_data.get("transect")
        width_m = cleaned_data.get("width_m")
        if transect and not width_m:
            msg = gettext(gettext('If there is a transect associated with this dive, you must provide a width.'))
            self.add_error('width_m', msg)



class SectionForm(forms.ModelForm):
    class Meta:
        model = models.Section
        fields = "__all__"
        exclude = ["dive"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = "form-control form-control-sm"

        self.fields["interval"].widget.attrs = {"v-model": "sectionToEdit.interval", "ref": "top_of_form", "@change": "unsavedSectionWork=true",
                                                ":disabled": "sectionToEdit.id", "class": klass}
        self.fields["depth_ft"].widget.attrs = {"v-model": "sectionToEdit.depth_ft", "min": 0, "@change": "unsavedSectionWork=true", "step": "0.01",
                                                "class": klass}
        self.fields["percent_sand"].widget.attrs = {"v-model": "sectionToEdit.percent_sand", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
                                                    "step": "0.01", "class": klass}
        self.fields["percent_mud"].widget.attrs = {"v-model": "sectionToEdit.percent_mud", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
                                                   "step": "0.01", "class": klass}
        self.fields["percent_hard"].widget.attrs = {"v-model": "sectionToEdit.percent_hard", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
                                                    "step": "0.01", "class": klass}
        self.fields["percent_algae"].widget.attrs = {"v-model": "sectionToEdit.percent_algae", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
                                                     "step": "0.01", "class": klass}
        self.fields["percent_gravel"].widget.attrs = {"v-model": "sectionToEdit.percent_gravel", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
                                                      "step": "0.01", "class": klass}
        self.fields["percent_cobble"].widget.attrs = {"v-model": "sectionToEdit.percent_cobble", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
                                                      "step": "0.01", "class": klass}
        self.fields["percent_pebble"].widget.attrs = {"v-model": "sectionToEdit.percent_pebble", "max": 1, "min": 0, "@change": "unsavedSectionWork=true",
                                                      "step": "0.01", "class": klass}
        self.fields["comment"].widget.attrs = {"v-model": "sectionToEdit.comment", "@change": "unsavedSectionWork=true", "row": 3, "class": klass}


class ObservationForm(forms.ModelForm):
    class Meta:
        model = models.Observation
        fields = "__all__"
        exclude = ["section"]
        widgets = {
            "comment": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = "form-control form-control-sm"
        self.fields["sex"].widget.attrs = {"v-model": "obs.sex", "@change": "updateObservation(obs)", "class": klass}
        self.fields["egg_status"].widget.attrs = {"v-model": "obs.egg_status", "@change": "updateObservation(obs)", "class": klass, ":disabled": "obs.sex!='f'"}
        self.fields["carapace_length_mm"].widget.attrs = {"v-model": "obs.carapace_length_mm", "@change": "updateObservation(obs)", "class": klass}
        self.fields["certainty_rating"].widget.attrs = {"v-model": "obs.certainty_rating", "@change": "updateObservation(obs)", "class": klass}
        self.fields["comment"].widget.attrs = {"v-model": "obs.comment", "@change": "updateObservation(obs)", "class": klass}


class NewObservationForm(forms.ModelForm):
    class Meta:
        model = models.Observation
        fields = "__all__"
        exclude = ["section"]
        widgets = {
            # "comment": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        klass = "form-control form-control-sm"
        self.fields["sex"].widget.attrs = {"v-model": "new_observation.sex", "ref": "top_of_form1", "class": klass,
                                           "@change": "updateEggStatus(new_observation)"}
        self.fields["egg_status"].widget.attrs = {"v-model": "new_observation.egg_status", "class": klass}
        self.fields["carapace_length_mm"].widget.attrs = {"v-model": "new_observation.carapace_length_mm", "class": klass,
                                                          "@change": "updateLengthCertainty(new_observation)"}
        self.fields["certainty_rating"].widget.attrs = {"v-model": "new_observation.certainty_rating", "class": klass}
        self.fields["comment"].widget.attrs = {"v-model": "new_observation.comment", "row": 3, "class": klass}


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "------"),
        (1, "dive log (xlsx)"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    year = forms.IntegerField(required=False, label=gettext_lazy('Year'), widget=forms.NumberInput(attrs={"placeholder": "Leave blank for all years"}))
