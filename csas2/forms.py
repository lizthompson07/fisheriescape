from django import forms
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy, gettext

from shared_models.models import Section, Person
from . import models

attr_fp_date = {"class": "fp-date", "placeholder": gettext_lazy("Click to select a date..")}
attr_fp_date_range = {"class": "fp-date-range", "placeholder": gettext_lazy("Click to select a range of dates..")}
multi_select_js = {"class": "multi-select"}
attr_fp_date_multiple = {"class": "fp-date-multiple", "placeholder": gettext_lazy("Click to select all applicable dates..")}
chosen_js = {"class": "chosen-select-contains"}
rows3 = {"rows": "3"}
YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "affiliation",
            "language",
            "dmapps_user",
        ]
        widgets = {
            'dmapps_user': forms.Select(attrs=chosen_js),
        }


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
            'client',
            'section',
            'coordinator',
            'language',
            'title',
            'is_carry_over',
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
            'advice_needed_by': forms.DateInput(attrs=dict(type="date")),
            'multiregional_text': forms.Textarea(attrs=rows3),
            'assistance_text': forms.Textarea(attrs=rows3),
            'funding_text': forms.Textarea(attrs=rows3),
            'risk_text': forms.Textarea(),
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
        client = cleaned_data.get("client")
        coordinator = cleaned_data.get("coordinator")
        section = cleaned_data.get("section")
        if not client:
            error_msg = gettext("Must enter a client for this request!")
            raise forms.ValidationError(error_msg)
        if not coordinator:
            error_msg = gettext("Must enter a coordinator for this request!")
            raise forms.ValidationError(error_msg)
        if not section:
            error_msg = gettext("Must enter a section for this request!")
            raise forms.ValidationError(error_msg)
        return self.cleaned_data


class TermsOfReferenceForm(forms.ModelForm):
    class Meta:
        model = models.TermsOfReference
        fields = "__all__"
        # widgets = {
        #     'decision_date': forms.DateInput(attrs=attr_fp_date),
        #     'advice_date': forms.DateInput(attrs=attr_fp_date),
        #     'prioritization_text': forms.Textarea(attrs=rows3),
        #     'decision_text': forms.Textarea(attrs=rows3),
        # }

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            process = kwargs.get("instance").process
        else:
            process = get_object_or_404(models.Process, pk=kwargs.get("initial").get("process"))
        meeting_choices = [(obj.id, f"{str(obj)}") for obj in process.meetings.all()]
        meeting_choices.insert(0, (None, "-----"))
        super().__init__(*args, **kwargs)
        self.fields["meeting"].choices = meeting_choices

    # def clean(self):
    #     cleaned_data = super().clean()
    #     # make sure that if a decision is given, there is a decision date as well
    #     decision = cleaned_data.get("decision")
    #     decision_date = cleaned_data.get("decision_date")
    #
    #     if decision and not decision_date:
    #         error_msg = gettext("If a decision was made, a decision date must also be populated!")
    #         self.add_error('decision_date', error_msg)
    #     return self.cleaned_data


class CSASRequestFileForm(forms.ModelForm):
    class Meta:
        model = models.CSASRequestFile
        fields = "__all__"


class ProcessForm(forms.ModelForm):
    class Meta:
        model = models.Process
        fields = [
            'name',
            'nom',
            'fiscal_year',
            'status',
            'scope',
            'type',
            'lead_region',
            'other_regions',
            'csas_requests',
            'coordinator',
            'advisors',
        ]
        widgets = {
            'csas_requests': forms.SelectMultiple(attrs=chosen_js),
            'advisors': forms.SelectMultiple(attrs=chosen_js),
            'coordinator': forms.Select(attrs=chosen_js),
            'lead_region': forms.Select(attrs=chosen_js),
            'other_regions': forms.SelectMultiple(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        request_choices = [(obj.id, f"{obj.id} - {str(obj)} {obj.ref_number} ({obj.fiscal_year})") for obj in
                           models.CSASRequest.objects.filter(submission_date__isnull=False)]
        super().__init__(*args, **kwargs)
        self.fields["csas_requests"].choices = request_choices

    def clean(self):
        cleaned_data = super().clean()
        # make sure that the lead_region is not also listed in the other_regions field
        lead_region = cleaned_data.get("lead_region")
        other_regions = cleaned_data.get("other_regions")

        if lead_region in other_regions:
            error_msg = gettext("Your lead region cannot be listed in the 'Other Regions' field.")
            self.add_error('other_regions', error_msg)
        return self.cleaned_data


class MeetingForm(forms.ModelForm):
    date_range = forms.CharField(widget=forms.TextInput(attrs=attr_fp_date_range), label=gettext_lazy("Meeting dates"), required=False,
                                 help_text=gettext_lazy("This can be left blank if not currently known"))

    class Meta:
        model = models.Meeting
        exclude = ["start_date", "end_date"]


class DocumentForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = "__all__"
        widgets = {
            'meetings': forms.SelectMultiple(attrs=multi_select_js),

        }


class SeriesForm(forms.ModelForm):
    class Meta:
        model = models.Series
        fields = "__all__"
        widgets = {
            # 'name': forms.Textarea(attrs={"rows": 3}),
            # 'nom': forms.Textarea(attrs={"rows": 3}),
        }


SeriesFormset = modelformset_factory(
    model=models.Series,
    form=SeriesForm,
    extra=1,
)


class InviteeRoleForm(forms.ModelForm):
    class Meta:
        model = models.InviteeRole
        fields = "__all__"
        widgets = {
            # 'name': forms.Textarea(attrs={"rows": 3}),
            # 'nom': forms.Textarea(attrs={"rows": 3}),
        }


InviteeRoleFormset = modelformset_factory(
    model=models.InviteeRole,
    form=InviteeRoleForm,
    extra=1,
)
