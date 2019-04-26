from django import forms
from django.db.models import Q
from django.utils.translation import gettext as _
from . import models
from django.contrib.auth.models import User
from shared_models import models as shared_models

class NewProjectForm(forms.ModelForm):
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
            'project_title': forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        SECTION_CHOICES = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.filter(Q(division__branch__region=1)|Q(division__branch__region=2)).order_by("division__branch__region", "division__branch", "division", "name")]
        SECTION_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = SECTION_CHOICES


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        exclude = [
            'submitted',
            'date_last_modified',
            'section_head_approved',
            'description_html',
            'priorities_html',
            'deliverables_html',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={"type": "date"}),
            'end_date': forms.DateInput(attrs={"type": "date"}),
            'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 5}),
            "description": forms.Textarea(attrs={"rows": 8}),
            "notes": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        SECTION_CHOICES = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.filter(Q(division__branch__region=1)|Q(division__branch__region=2)).order_by("division__branch__region", "division__branch", "division", "name")]
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
    REPORT_CHOICES = (
        (3, "Project Summary Report (PDF)"),
        (2, "Batch Workplan Export (PDF) (submitted and approved)"),
        (1, "Master spreadsheet (XLSX)"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    fiscal_year = forms.ChoiceField(required=True)
    sections = forms.MultipleChoiceField(required=False, label="Sections (Leave blank to select all)")

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

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
