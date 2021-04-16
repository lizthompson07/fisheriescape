from django import forms
from django.utils.translation import gettext_lazy, gettext

from shared_models.models import Section
from . import models

attr_fp_date = {"class": "fp-date", "placeholder": gettext_lazy("Click to select a date..")}
chosen_js = {"class": "chosen-select-contains"}
rows3 = {"rows": "3"}
YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "------"),
        (1, "------"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    year = forms.IntegerField(required=False, label=gettext_lazy('Year'), widget=forms.NumberInput(attrs={"placeholder": "Leave blank for all years"}))


class CSASRequestForm(forms.ModelForm):
    class Meta:
        model = models.CSASRequest
        fields = [
            'type',
            'language',
            'name',
            'nom',
            'coordinator',
            'client',
            'section',
            'is_multiregional',
            'multiregional_text',
            'issue',
            'had_assistance',
            'assistance_text',
            'rationale',
            'risk_text',
            'advice_needed_by',
            'rationale_for_timeline',
            'has_funding',
            'funding_text',
        ]
        widgets = {
            'client': forms.Select(attrs=chosen_js),
            'coordinator': forms.Select(attrs=chosen_js),
            'section': forms.Select(attrs=chosen_js),
            'advice_needed_by': forms.DateInput(attrs=attr_fp_date),
            'multiregional_text': forms.Textarea(attrs=rows3),
            'assistance_text': forms.Textarea(attrs=rows3),
            'funding_text': forms.Textarea(attrs=rows3),
            'rationale_for_timeline': forms.Textarea(attrs=rows3),
        }

    def __init__(self, *args, **kwargs):
        section_choices = [(obj.id, obj.full_name) for obj in Section.objects.all()]
        section_choices.insert(0, (None, "------"))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = section_choices

    def clean(self):
        cleaned_data = super().clean()
        # make sure there is at least an english or french title
        name = cleaned_data.get("end_date")
        nom = cleaned_data.get("det_valid")
        if not name and not nom:
            error_msg = gettext("Must have either an English title or a French title!")
            self.add_error('name', error_msg)
            self.add_error('nom', error_msg)
            raise forms.ValidationError(error_msg)
        return self.cleaned_data