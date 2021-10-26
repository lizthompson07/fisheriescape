from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy, gettext

from lib.templatetags.custom_filters import nz
from shared_models.models import Section, Person, FiscalYear, SubjectMatter
from . import models, model_choices, utils

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
            "expertise",
        ]
        widgets = {
            'dmapps_user': forms.Select(attrs=chosen_js),
            'expertise': forms.SelectMultiple(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("instance") and kwargs.get("instance").dmapps_user:
            del self.fields["first_name"]
            del self.fields["last_name"]
            del self.fields["phone"]
            del self.fields["email"]
            del self.fields["affiliation"]
            del self.fields["language"]
            del self.fields["dmapps_user"]


class TripRequestTimestampUpdateForm(forms.ModelForm):
    class Meta:
        model = models.CSASRequest
        fields = [
            "is_multiregional",  # just a random field
        ]
        widgets = {
            "is_multiregional": forms.HiddenInput()
        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "------"),
        (1, "Meetings for Website (Excel)"),
        (2, "CSAS Request batch export (PDF)"),
        (3, "CSAS Request list (Excel)"),
        (4, "State of Our Processes (Excel)"),
        (999, "Participant List (Excel) --> placeholder"),
        (999, "Process Cost Report (Excel) --> placeholder"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    fiscal_year = forms.ChoiceField(required=False, label=gettext_lazy('Fiscal year'))
    is_posted = forms.ChoiceField(required=False, label=gettext_lazy('Posted processes?'))
    request_status = forms.ChoiceField(required=False, label=gettext_lazy('Request Status'))
    process_status = forms.ChoiceField(required=False, label=gettext_lazy('Process Status'))
    process_type = forms.ChoiceField(required=False, label=gettext_lazy('Process Type'))

    region = forms.ChoiceField(required=False, label=gettext_lazy('DFO Region'))
    sector = forms.ChoiceField(required=False, label=gettext_lazy('DFO Sector'))
    branch = forms.ChoiceField(required=False, label=gettext_lazy('DFO Branch'))
    division = forms.ChoiceField(required=False, label=gettext_lazy('DFO Division'))
    section = forms.ChoiceField(required=False, label=gettext_lazy('DFO Section'))
    csas_requests = forms.MultipleChoiceField(required=False, label=gettext_lazy('CSAS Requests'), help_text=gettext("leave blank for all"),
                                              widget=forms.SelectMultiple(attrs=dict(style="height: 200px")))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        posted_choices = (
            ("", "All meetings"),
            (1, gettext("Only posted")),
            (0, gettext("Only un-posted")),
        )
        fy_choices = [(obj.id, str(obj)) for obj in FiscalYear.objects.filter(Q(processes__isnull=False) | Q(csas_requests__isnull=False)).distinct()]
        fy_choices.insert(0, (None, "All"))

        request_status_choices = [obj for obj in model_choices.request_status_choices]
        request_status_choices.insert(0, (None, "All"))

        request_choices = [(obj.id, f"{obj.id} - {obj.title}") for obj in models.CSASRequest.objects.all()]

        region_choices = utils.get_region_choices(with_requests=True)
        region_choices.insert(0, (None, "All"))

        branch_choices = utils.get_branch_choices(with_requests=True)
        branch_choices.insert(0, (None, "All"))

        sector_choices = utils.get_sector_choices(with_requests=True)
        sector_choices.insert(0, (None, "All"))

        division_choices = utils.get_division_choices(with_requests=True)
        division_choices.insert(0, (None, "All"))

        section_choices = utils.get_section_choices(with_requests=True)
        section_choices.insert(0, (None, "All"))

        self.fields["fiscal_year"].choices = fy_choices
        self.fields["is_posted"].choices = posted_choices
        self.fields["request_status"].choices = request_status_choices
        self.fields["csas_requests"].choices = request_choices

        self.fields['region'].choices = region_choices
        self.fields['sector'].choices = sector_choices
        self.fields['branch'].choices = branch_choices
        self.fields['division'].choices = division_choices
        self.fields['section'].choices = section_choices


class CSASRequestForm(forms.ModelForm):
    class Meta:
        model = models.CSASRequest
        fields = [
            'client',
            'section',
            'coordinator',
            'language',
            'title',
            'is_multiregional',
            'multiregional_text',
            'issue',
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
        required_fields = [
            'client',
            'title',
            'section',
            'coordinator',
            'advice_needed_by',
        ]
        widgets = {
            'client': forms.Select(attrs=chosen_js),
            'coordinator': forms.Select(attrs=chosen_js),
            'section': forms.Select(attrs=chosen_js),
            'advice_needed_by': forms.DateInput(attrs=dict(type="date"), format="%Y-%m-%d"),
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
        coordinator_choices = [(u.id, u.get_full_name()) for u in User.objects.filter(groups__name__in=["csas_regional_admin", "csas_national_admin"])]
        coordinator_choices.insert(0, (None, "------"))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = section_choices
        self.fields['coordinator'].choices = coordinator_choices

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

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            csas_request = kwargs.get("instance").csas_request
        else:
            csas_request = get_object_or_404(models.CSASRequest, pk=kwargs.get("initial").get("csas_request"))

        super().__init__(*args, **kwargs)
        if not csas_request.submission_date:
            del self.fields["is_approval"]


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
    create_steering_committee_meeting = forms.BooleanField(
        help_text=gettext_lazy("By checking this box, a draft steering committee meeting will be automatically created upon submitting this form."),
        label=gettext_lazy("Create a placeholder steering committee meeting?"),
        required=False,
    )
    committee_members = forms.MultipleChoiceField(
        help_text=gettext_lazy("These individuals will be added as meeting invitees and tagged with the role of 'Steering Committee Member'."),
        label=gettext_lazy("Steering committee members"),
        widget=forms.SelectMultiple(attrs=chosen_js),
        required=False,
    )
    create_keystone_meeting = forms.BooleanField(
        help_text=gettext_lazy("By checking this box, a draft keystone meeting will be automatically created upon submitting this form."),
        label=gettext_lazy("Create a placeholder keystone meeting?"),
        required=False,
    )
    science_leads = forms.MultipleChoiceField(
        help_text=gettext_lazy("These individuals will be added as meeting invitees and tagged with the role of 'Science Lead'."),
        label=gettext_lazy("Science leads"),
        widget=forms.SelectMultiple(attrs=chosen_js),
        required=False,
    )
    client_leads = forms.MultipleChoiceField(
        help_text=gettext_lazy("These individuals will be added as meeting invitees and tagged with the role of 'Client Lead'."),
        label=gettext_lazy("Client leads"),
        widget=forms.SelectMultiple(attrs=chosen_js),
        required=False,
    )
    chair = forms.ChoiceField(
        help_text=gettext_lazy("This individual will be added as a meeting invitee and tagged with the role of 'chair'."),
        label=gettext_lazy("Chair"),
        widget=forms.Select(attrs=chosen_js),
        required=False,
    )

    class Meta:
        model = models.Process
        fields = [
            'csas_requests',
            'name',
            'nom',
            'advice_date',
            'status',
            'scope',
            'type',
            'lead_region',
            'other_regions',
            'coordinator',
            'advisors',
            'editors',
        ]
        required_fields = [
            'csas_requests',
            gettext_lazy('name'),
            'scope',
            'type',
            'coordinator',
            'lead_region',
        ]
        widgets = {
            'csas_requests': forms.SelectMultiple(attrs=chosen_js),
            'advisors': forms.SelectMultiple(attrs=chosen_js),
            'editors': forms.SelectMultiple(attrs=chosen_js),
            'coordinator': forms.Select(attrs=chosen_js),
            'lead_region': forms.Select(attrs=chosen_js),
            'other_regions': forms.SelectMultiple(attrs=chosen_js),
            'advice_date': forms.DateInput(attrs=dict(type="date"), format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        request_choices = [(obj.id, f"{obj.id} - {str(obj)} {nz(obj.ref_number, '')} ({obj.fiscal_year})") for obj in
                           models.CSASRequest.objects.filter(submission_date__isnull=False)]
        super().__init__(*args, **kwargs)
        self.fields["csas_requests"].choices = request_choices
        if kwargs.get("instance"):
            del self.fields["create_steering_committee_meeting"]
            del self.fields["science_leads"]
        else:
            person_choices = [(p.id, f"{p} ({p.email})") for p in Person.objects.all()]
            self.fields["committee_members"].choices = person_choices
            self.fields["science_leads"].choices = person_choices
            self.fields["client_leads"].choices = person_choices
            person_choices.insert(0, (None, "-----"))
            self.fields["chair"].choices = person_choices

    def clean(self):
        cleaned_data = super().clean()
        # make sure that the lead_region is not also listed in the other_regions field
        lead_region = cleaned_data.get("lead_region")
        other_regions = cleaned_data.get("other_regions")
        coordinator = cleaned_data.get("coordinator")
        lead_region = cleaned_data.get("lead_region")
        name = cleaned_data.get("name")
        nom = cleaned_data.get("nom")
        if not name and not nom:
            error_msg = gettext("Must have either an English title or a French title!")
            self.add_error('name', error_msg)
            self.add_error('nom', error_msg)
            raise forms.ValidationError(error_msg)
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
        "is_estimate",
    ]
    date_range = forms.CharField(widget=forms.TextInput(attrs=attr_fp_date_range), label=gettext_lazy("Meeting dates"), required=True,
                                 help_text=gettext_lazy("You can provide an approximate date."))

    class Meta:
        model = models.Meeting
        exclude = ["start_date", "end_date"]


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


class TagForm(forms.ModelForm):
    class Meta:
        model = SubjectMatter
        fields = "__all__"


TagFormset = modelformset_factory(
    model=SubjectMatter,
    form=TagForm,
    extra=1,
)


class CSASAdminUserForm(forms.ModelForm):
    class Meta:
        model = models.CSASAdminUser
        fields = "__all__"
        widgets = {
            'user': forms.Select(attrs=chosen_js),
        }


CSASAdminUserFormset = modelformset_factory(
    model=models.CSASAdminUser,
    form=CSASAdminUserForm,
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
