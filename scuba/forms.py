from django import forms
from django.forms import modelformset_factory

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


class DiveForm(forms.ModelForm):
    # field_order = ["name"]
    class Meta:
        model = models.Dive
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("instance"):
            self.fields["transect"].queryset = kwargs.get("instance").sample.site.transects.all()
        elif kwargs.get("initial"):
            self.fields["transect"].queryset = models.Sample.objects.get(pk=kwargs.get("initial").get("sample")).site.transects.all()
