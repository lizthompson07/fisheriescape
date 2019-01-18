from django import forms
from django.core import validators
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
    pass
    # SPECIES_CHOICES = ((None, "---"),)
    # for obj in models.Species.objects.all().order_by("common_name_eng"):
    #     SPECIES_CHOICES = SPECIES_CHOICES.__add__(((obj.id, obj),))
    #
    # SITE_CHOICES = ((None, "All Stations"),)
    # for obj in models.Site.objects.all():
    #     SITE_CHOICES = SITE_CHOICES.__add__(((obj.id, obj),))
    #
    # REPORT_CHOICES = (
    #     (None, "---"),
    #     (1, "Species counts by year"),
    #     (2, "Species richness by year"),
    #     (3, "Annual watershed report (PDF)"),
    #     (4, "Annual watershed spreadsheet (XLSX)"),
    #     (5, "Dataset export for FGP (CSV)"),
    # )
    #
    # report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    # species = forms.MultipleChoiceField(required=False, choices=SPECIES_CHOICES)
    # year = forms.CharField(required=False, widget=forms.NumberInput())
    # site = forms.ChoiceField(required=False, choices=SITE_CHOICES)
