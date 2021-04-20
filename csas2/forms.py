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


class TripRequestTimestampUpdateForm(forms.ModelForm):
    class Meta:
        model = models.CSASRequest
        fields = [
            "notes",
        ]
        widgets = {
            "notes": forms.HiddenInput()
        }


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
            'prioritization',
            'prioritization_text',
        ]
        widgets = {
            'client': forms.Select(attrs=chosen_js),
            'coordinator': forms.Select(attrs=chosen_js),
            'section': forms.Select(attrs=chosen_js),
            'advice_needed_by': forms.DateInput(attrs=attr_fp_date),
            'multiregional_text': forms.Textarea(attrs=rows3),
            'assistance_text': forms.Textarea(attrs=rows3),
            'funding_text': forms.Textarea(attrs=rows3),
            'risk_text': forms.Textarea(attrs=rows3),
            'rationale_for_timeline': forms.Textarea(attrs=rows3),
            'prioritization_text': forms.Textarea(attrs=rows3),
        }

    def __init__(self, *args, **kwargs):
        section_choices = [(obj.id, obj.full_name) for obj in Section.objects.all()]
        section_choices.insert(0, (None, "------"))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = section_choices

    def clean(self):
        cleaned_data = super().clean()
        # make sure there is at least an english or french title
        name = cleaned_data.get("name")
        nom = cleaned_data.get("nom")
        if not name and not nom:
            error_msg = gettext("Must have either an English title or a French title!")
            raise forms.ValidationError(error_msg)
        return self.cleaned_data


class CSASRequestReviewForm(forms.ModelForm):
    class Meta:
        model = models.CSASRequestReview
        fields = "__all__"
        widgets = {
            'decision_date': forms.DateInput(attrs=attr_fp_date),
            'prioritization_text': forms.Textarea(attrs=rows3),
            'decision_text': forms.Textarea(attrs=rows3),
        }

    def clean(self):
        cleaned_data = super().clean()
        # make sure that if a decision is given, there is a decision date as well
        decision = cleaned_data.get("decision")
        decision_date = cleaned_data.get("decision_date")

        if decision and not decision_date:
            error_msg = gettext("If a decision was made, a decision date must also be populated!")
            self.add_error('decision_date', error_msg)
        return self.cleaned_data


class CSASRequestFileForm(forms.ModelForm):
    class Meta:
        model = models.CSASRequestFile
        fields = "__all__"


class ProcessForm(forms.ModelForm):
    class Meta:
        model = models.Process
        fields = "__all__"
        widgets = {
            'csas_requests': forms.SelectMultiple(attrs=chosen_js),
            'advisors': forms.SelectMultiple(attrs=chosen_js),
            'coordinator': forms.Select(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        request_choices = [(obj.id, f"{obj.id} - {str(obj)}") for obj in models.CSASRequest.objects.all()]
        super().__init__(*args, **kwargs)
        self.fields["csas_requests"].choices = request_choices
