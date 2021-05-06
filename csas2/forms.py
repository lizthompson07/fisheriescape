from django import forms
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy, gettext

from lib.templatetags.custom_filters import nz
from shared_models.models import Section, Person, FiscalYear
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
        (1, "Meetings for Website"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    fiscal_year = forms.ChoiceField(required=False, label=gettext_lazy('Fiscal year'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fy_choices = [(obj.id, str(obj)) for obj in FiscalYear.objects.filter(processes__isnull=False).distinct()]
        fy_choices.insert(0, (None, "-----"))
        self.fields["fiscal_year"].choices = fy_choices


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
        widgets = {
            'expected_document_types': forms.SelectMultiple(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            process = kwargs.get("instance").process
        else:
            process = get_object_or_404(models.Process, pk=kwargs.get("initial").get("process"))
        meeting_choices = [(obj.id, f"{str(obj)}") for obj in process.meetings.all()]
        meeting_choices.insert(0, (None, "-----"))
        document_type_choices = [(obj.id, f"{str(obj)}") for obj in models.DocumentType.objects.filter(hide_from_list=False)]
        document_type_choices.insert(0, (None, "-----"))

        super().__init__(*args, **kwargs)
        self.fields["meeting"].choices = meeting_choices
        self.fields["expected_document_types"].choices = document_type_choices

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


class MeetingFileForm(forms.ModelForm):
    class Meta:
        model = models.MeetingFile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("instance"):
            meeting = kwargs.get("instance").meeting
        else:
            meeting = get_object_or_404(models.Meeting, pk=kwargs.get("initial").get("meeting"))
        if meeting.is_planning:
            del self.fields["is_somp"]

class ProcessForm(forms.ModelForm):
    class Meta:
        model = models.Process
        fields = [
            'csas_requests',
            'name',
            'nom',
            'fiscal_year',
            'status',
            'scope',
            'type',
            'lead_region',
            'other_regions',
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
        request_choices = [(obj.id, f"{obj.id} - {str(obj)} {nz(obj.ref_number,'')} ({obj.fiscal_year})") for obj in
                           models.CSASRequest.objects.filter(submission_date__isnull=False)]
        super().__init__(*args, **kwargs)
        self.fields["csas_requests"].choices = request_choices

    def clean(self):
        cleaned_data = super().clean()
        # make sure that the lead_region is not also listed in the other_regions field
        lead_region = cleaned_data.get("lead_region")
        other_regions = cleaned_data.get("other_regions")
        coordinator = cleaned_data.get("coordinator")
        lead_region = cleaned_data.get("lead_region")

        if lead_region in other_regions:
            error_msg = gettext("Your lead region cannot be listed in the 'Other Regions' field.")
            self.add_error('other_regions', error_msg)
        if not coordinator:
            error_msg = gettext("Must enter a coordinator for this request!")
            raise forms.ValidationError(error_msg)
        if not lead_region:
            error_msg = gettext("Must enter a lead region for this process!")
            raise forms.ValidationError(error_msg)
        return self.cleaned_data


class MeetingForm(forms.ModelForm):
    field_order = [
        "name",
        "nom",
        "is_planning",
        "is_virtual",
        "location",
        "date_range",
        "est_quarter",
        "est_year",
    ]
    date_range = forms.CharField(widget=forms.TextInput(attrs=attr_fp_date_range), label=gettext_lazy("Meeting dates"), required=False,
                                 help_text=gettext_lazy("This can be left blank if not currently known"))

    class Meta:
        model = models.Meeting
        exclude = ["start_date", "end_date"]

    def clean(self):
        cleaned_data = super().clean()
        # make sure that the lead_region is not also listed in the other_regions field
        date_range = cleaned_data.get("date_range")
        est_quarter = cleaned_data.get("est_quarter")
        est_year = cleaned_data.get("est_year")

        if not date_range and (not est_year or not est_quarter):
            error_msg = gettext("Must enter either a date range OR an estimated quarter / year!")
            raise forms.ValidationError(error_msg)
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meeting_quarter_choices = (
            (None, "-----"),
            (1, gettext("Spring (April - June)")),
            (2, gettext("Summer (July - September)")),
            (3, gettext("Fall (October - December)")),
            (4, gettext("Winter (January - March)")),
        )
        self.fields["est_quarter"].choices = meeting_quarter_choices


class DocumentForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = "__all__"
        widgets = {
            'meetings': forms.SelectMultiple(attrs=chosen_js),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("instance"):
            process = kwargs.get("instance").process
        else:
            process = get_object_or_404(models.Process, pk=kwargs.get("initial").get("process"))
        # meeting_choices
        meeting_choices = [(obj.id, f"{str(obj)}") for obj in process.meetings.all()]
        meeting_choices.insert(0, (None, "-----"))
        self.fields["meetings"].choices = meeting_choices

        if not kwargs.get("instance"):
            del self.fields["year"]
            del self.fields["pages"]
            del self.fields["url_en"]
            del self.fields["url_fr"]
            del self.fields["file_en"]
            del self.fields["file_fr"]
            del self.fields["dev_link_en"]
            del self.fields["dev_link_fr"]
            del self.fields["ekme_gcdocs_en"]
            del self.fields["ekme_gcdocs_fr"]
            del self.fields["lib_cat_en"]
            del self.fields["lib_cat_fr"]


class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = models.DocumentType
        fields = "__all__"
        widgets = {
            # 'name': forms.Textarea(attrs={"rows": 3}),
            # 'nom': forms.Textarea(attrs={"rows": 3}),
        }


DocumentTypeFormset = modelformset_factory(
    model=models.DocumentType,
    form=DocumentTypeForm,
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
