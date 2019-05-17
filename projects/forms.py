from django import forms
from django.db.models import Q
from django.utils.translation import gettext as _
from . import models
from django.contrib.auth.models import User
from shared_models import models as shared_models

chosen_js = {"class": "chosen-select-contains"}


class NewProjectForm(forms.ModelForm):
    region = forms.ChoiceField()
    division = forms.ChoiceField()
    field_order = ['year', 'project_title', 'region', 'division', 'section']

    class Meta:
        model = models.Project
        fields = [
            'year',
            'project_title',
            'section',
            'last_modified_by',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        region_choices = [(r.id, str(r)) for r in shared_models.Region.objects.filter(Q(id=1) | Q(id=2))]
        region_choices.insert(0, tuple((None, "---")))

        division_choices = [(d.id, str(d)) for d in
                            shared_models.Division.objects.filter(Q(branch_id=1) | Q(branch_id=3)).order_by("branch__region", "name")]
        division_choices.insert(0, tuple((None, "---")))

        section_choices = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.filter(Q(division__branch_id=1) | Q(division__branch_id=3)).order_by(
                               "division__branch__region", "division__branch", "division", "name")]
        section_choices.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['region'].choices = region_choices
        self.fields['division'].choices = division_choices
        self.fields['section'].choices = section_choices


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        exclude = [
            'submitted',
            'date_last_modified',
            'section_head_approved',
            'description',
            'priorities',
            'deliverables',
        ]
        class_editable = {"class": "editable"}
        widgets = {
            "project_title": forms.Textarea(attrs={"rows":"3"}),

            "description_html": forms.Textarea(attrs=class_editable),
            "priorities_html": forms.Textarea(attrs=class_editable),
            "deliverables_html": forms.Textarea(attrs=class_editable),
            "data_collection": forms.Textarea(attrs=class_editable),
            "data_sharing": forms.Textarea(attrs=class_editable),
            "data_storage": forms.Textarea(attrs=class_editable),
            "regional_dm_needs": forms.Textarea(attrs=class_editable),
            "sectional_dm_needs": forms.Textarea(attrs=class_editable),
            "vehicle_needs": forms.Textarea(attrs=class_editable),
            "it_needs": forms.Textarea(attrs=class_editable),
            "chemical_needs": forms.Textarea(attrs=class_editable),
            "ship_needs": forms.Textarea(attrs=class_editable),
            "feedback": forms.Textarea(attrs=class_editable),

            'start_date': forms.DateInput(attrs={"type": "date"}),
            'end_date': forms.DateInput(attrs={"type": "date"}),
            'last_modified_by': forms.HiddenInput(),
            "section": forms.Select(attrs=chosen_js),
            "program": forms.Select(attrs=chosen_js),
            "responsibility_center": forms.Select(attrs=chosen_js),
            "allotment_code": forms.Select(attrs=chosen_js),
            "existing_project_code": forms.Select(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        SECTION_CHOICES = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.filter(Q(division__branch__region=1) | Q(division__branch__region=2)).order_by(
                               "division__branch__region", "division__branch", "division", "name")]
        SECTION_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = SECTION_CHOICES


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
    save_then_go_OT = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = models.Staff
        fields = "__all__"
        labels = {
            "user": _("DFO User"),
        }
        widgets = {
            'project': forms.HiddenInput(),
            'overtime_description': forms.Textarea(attrs={"rows": 5}),
            'user': forms.Select(attrs=chosen_js),
        }



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
    REPORT_CHOICES = (
        (3, "Project Summary Report (PDF)"),
        (2, "Batch Workplan Export (PDF) (submitted and approved)"),
        (1, "Master spreadsheet (XLSX)"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    fiscal_year = forms.ChoiceField(required=True)
    sections = forms.MultipleChoiceField(required=False, label="Sections (Leave blank to select all)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all()]
        section_choices = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.filter(Q(division__branch__region=1) | Q(division__branch__region=2)).order_by(
                               "division__branch__region", "division__branch", "division", "name")]
        self.fields["sections"].choices = section_choices
        self.fields["fiscal_year"].choices = fy_choices


class OTForm(forms.ModelForm):
    class Meta:
        model = models.Staff
        fields = ["overtime_hours", "overtime_description"]
        widgets = {
            'overtime_hours': forms.HiddenInput(),
            'overtime_description': forms.HiddenInput(),
        }


class UserCreateForm(forms.Form):
    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))
    email1 = forms.EmailField(label=_("Email"))
    email2 = forms.EmailField(label=_("Confirm email address"))

    def clean_email1(self):
        new_email = self.cleaned_data['email1']
        # check to make sure is not a duplicate
        if User.objects.filter(email__iexact=new_email).count() > 0:
            raise forms.ValidationError("This email address already exists in the database.")
        # check to make sure is a DFO email
        if new_email.lower().endswith("@dfo-mpo.gc.ca") == False:
            raise forms.ValidationError(_("The email address provided must be a DFO email address."))

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return new_email

    def clean(self):
        cleaned_data = super().clean()
        first_email = cleaned_data.get("email1")
        second_email = cleaned_data.get("email2")

        if first_email and second_email:
            # Only do something if both fields are valid so far.

            # verify the two emails are the same
            if first_email.lower() != second_email.lower():
                raise forms.ValidationError(_("Please make sure the two email addresses provided match."))
