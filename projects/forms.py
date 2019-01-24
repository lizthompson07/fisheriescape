from django import forms
from django.core import validators
from django.utils import timezone
from django.utils.translation import gettext as _
from . import models
from django.contrib.auth.models import User


class NewProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = [
            'fiscal_year',
            'project_title',
            'section',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={"type": "date"}),
            'end_date': forms.DateInput(attrs={"type": "date"}),
            'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 5}),
            "description": forms.Textarea(attrs={"rows": 8}),
            "notes": forms.Textarea(attrs={"rows": 5}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        exclude = [
            'last_modified_by',
            'submitted',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={"type": "date"}),
            'end_date': forms.DateInput(attrs={"type": "date"}),
            'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 5}),
            "description": forms.Textarea(attrs={"rows": 8}),
            "notes": forms.Textarea(attrs={"rows": 5}),
        }


class ProjectSubmitForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = [
            'last_modified_by',
            'submitted',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'submitted': forms.HiddenInput(),
        }


class StaffForm(forms.ModelForm):
    class Meta:
        model = models.Staff
        fields = "__all__"
        widgets = {
            'project': forms.HiddenInput(),
            'overtime_description': forms.Textarea(attrs={"rows": 4}),
            # 'user': forms.Select(choices=USER_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        User.objects.all().order_by("last_name", "first_name")]
        USER_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all().order_by("last_name", "first_name")
        self.fields['user'].choices = USER_CHOICES


class CollaboratorForm(forms.ModelForm):
    class Meta:
        model = models.Collaborator
        fields = "__all__"
        widgets = {
            'project': forms.HiddenInput(),
        }


class AgreementForm(forms.ModelForm):
    class Meta:
        model = models.CollaborativeAgreement
        fields = "__all__"
        widgets = {
            'project': forms.HiddenInput(),
        }


class OMCostForm(forms.ModelForm):
    class Meta:
        model = models.OMCost
        fields = "__all__"
        widgets = {
            'project': forms.HiddenInput(),
        }


class CapitalCostForm(forms.ModelForm):
    class Meta:
        model = models.CapitalCost
        fields = "__all__"
        widgets = {
            'project': forms.HiddenInput(),
        }


class GCCostForm(forms.ModelForm):
    class Meta:
        model = models.GCCost
        fields = "__all__"
        widgets = {
            'project': forms.HiddenInput(),
        }


class ReportSearchForm(forms.Form):
    FY_CHOICES = [("{}-{}".format(y, y + 1), "{}-{}".format(y, y + 1)) for y in
                  range(timezone.now().year - 2, timezone.now().year + 1)]

    REPORT_CHOICES = (
        (1, "Regional Project Planning Summary"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    fiscal_year = forms.ChoiceField(required=True, choices=FY_CHOICES)


class OTForm(forms.ModelForm):
    # weekdays = forms.CharField(required=True, label=_(
    #     "Total number of weekday hours to be worked beyond 7.5 hours standard working day"), widget=forms.NumberInput())
    # saturdays = forms.CharField(required=True, label=_(
    #     "Total number of hours to be worked on Saturdays (enter all hours to be worked)"), widget=forms.NumberInput())
    # sundays = forms.CharField(required=True,
    #                           label=_("Total number of hours to be worked on Sundays (enter all hours to be worked)"),
    #                           widget=forms.NumberInput())
    # stat_holidays = forms.CharField(required=True, label=_(
    #     "Total number of hours to be worked on statutory holidays (enter all hours to be worked)"),
    #                                 widget=forms.NumberInput())

    class Meta:
        model = models.Staff
        fields = ["overtime_hours", "overtime_description"]
        widgets = {
            'overtime_hours': forms.HiddenInput(),
            'overtime_description': forms.HiddenInput(),
        }
