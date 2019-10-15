from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext as _
from django.contrib.auth.models import User as AuthUser
from shared_models import models as shared_models

from . import models

chosen_js = {"class": "chosen-select-contains"}
attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class EventApprovalForm(forms.Form):
    is_approved = forms.BooleanField(widget=forms.HiddenInput(), required=False)


class EventForm(forms.ModelForm):
    stay_on_page = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.Event
        exclude = [
            "total_cost",
            "fiscal_year",
            "recommender_1_approval_date",
            "recommender_1_approval_status",
            "recommender_2_approval_date",
            "recommender_2_approval_status",
            "recommender_3_approval_date",
            "recommender_3_approval_status",
            "approver_approval_date",
            "approver_approval_status",
            "waiting_on",
            "submitted",
            "status",
        ]
        labels = {
            'bta_attendees': _("Other attendees covered under BTA (i.e., they will not need to have a travel plan)"),
            'approver': _("Approver (i.e., usually the RDG)"),
        }
        widgets = {
            'start_date': forms.DateInput(attrs=attr_fp_date),
            'end_date': forms.DateInput(attrs=attr_fp_date),
            'bta_attendees': forms.SelectMultiple(attrs=chosen_js),
            'user': forms.Select(attrs=chosen_js),
            'recommender_1': forms.Select(attrs=chosen_js),
            'recommender_2': forms.Select(attrs=chosen_js),
            'recommender_3': forms.Select(attrs=chosen_js),
            'approver': forms.Select(attrs=chosen_js),
            'section': forms.Select(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        user_choices = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        AuthUser.objects.all().order_by("last_name", "first_name")]
        user_choices.insert(0, tuple((None, "---")))

        section_heads = [section.head for section in shared_models.Section.objects.filter(head__isnull=False)]
        division_heads = [division.head for division in shared_models.Division.objects.filter(head__isnull=False)]
        branch_heads = [branch.head for branch in shared_models.Branch.objects.filter(head__isnull=False)]
        region_heads = [region.head for region in shared_models.Region.objects.filter(head__isnull=False)]

        heads = []
        heads.extend(section_heads)
        heads.extend(division_heads)
        heads.extend(branch_heads)
        heads.extend(region_heads)
        heads = set(heads)

        recommender_chocies = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                               AuthUser.objects.all().order_by("last_name", "first_name") if u in heads]
        recommender_chocies.insert(0, tuple((None, "---")))

        section_choices = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.filter(division__branch_id=1).order_by("division__branch__region",
                                                                                                "division__branch",
                                                                                                "division", "name")]
        section_choices.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['user'].choices = user_choices
        self.fields['bta_attendees'].choices = user_choices
        self.fields['recommender_1'].choices = recommender_chocies
        self.fields['recommender_2'].choices = recommender_chocies
        self.fields['recommender_3'].choices = recommender_chocies
        self.fields['approver'].choices = recommender_chocies
        self.fields['section'].choices = section_choices


class RegisteredEventForm(forms.ModelForm):
    class Meta:
        model = models.RegisteredEvent
        fields = "__all__"
        widgets = {
            'start_date': forms.DateInput(attrs=attr_fp_date),
            'end_date': forms.DateInput(attrs=attr_fp_date),
        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "------"),
        (1, "CFTS export (xlsx)"),
        # (2, "Print Travel Plan PDF"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    # report #1
    fiscal_year = forms.ChoiceField(required=False, label=_('Fiscal year'))
    # report #2
    traveller = forms.ChoiceField(required=False, label=_('traveller'))

    def __init__(self, *args, **kwargs):
        FY_CHOICES = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all().order_by("id")]
        TRAVELLER_CHOICES = [(e['email'], "{}, {}".format(e['last_name'], e['first_name'])) for e in
                             models.Event.objects.values("email", "first_name", "last_name").order_by("last_name", "first_name").distinct()]
        super().__init__(*args, **kwargs)
        self.fields['fiscal_year'].choices = FY_CHOICES
        self.fields['traveller'].choices = TRAVELLER_CHOICES


class StatusForm(forms.ModelForm):
    class Meta:
        model = models.Status
        fields = "__all__"


StatusFormSet = modelformset_factory(
    model=models.Status,
    form=StatusForm,
    extra=1,
)
