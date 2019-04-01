from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from shared_models import models as shared_models
from . import models


class ResponsibilityCentreForm(forms.ModelForm):
    class Meta:
        model = shared_models.ResponsibilityCenter
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        User.objects.all().order_by("last_name", "first_name")]
        USER_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['manager'].choices = USER_CHOICES


class LineObjectForm(forms.ModelForm):
    class Meta:
        model = shared_models.LineObject
        fields = "__all__"


class BusinessLineForm(forms.ModelForm):
    class Meta:
        model = shared_models.BusinessLine
        fields = "__all__"


class AllotmentCodeForm(forms.ModelForm):
    class Meta:
        model = shared_models.AllotmentCode
        fields = "__all__"


class ProjectForm(forms.ModelForm):
    class Meta:
        model = shared_models.Project
        fields = "__all__"


class TransactionForm(forms.ModelForm):
    do_another = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.Transaction
        exclude = ["outstanding_obligation"]
        labels = {
            "fiscal_year": "Fiscal year (SAP style e.g. 2018-2019 = 2019)",
        }
        widgets = {
            "fiscal_year": forms.NumberInput(),
            "created_by": forms.HiddenInput(),
            "creation_date": forms.DateInput(attrs={"type": "date"}),
            "invoice_date": forms.DateInput(attrs={"type": "date"}),
        }


class CustomTransactionForm(forms.ModelForm):
    do_another = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.Transaction
        fields = [
            "project",
            "responsibility_center",
            "business_line",
            "allotment_code",
            "line_object",
            "supplier_description",
            "obligation_cost",
            "reference_number",
            "comment",

            # hidden fields
            "created_by",
            "creation_date",
            "transaction_type",
            "in_mrs",
        ]

        labels = {
            "supplier_description": "Expense description",
            "obligation_cost": "Cost estimation",
        }

        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4}),

            # hidden because they are given default values
            "created_by": forms.HiddenInput(),
            "creation_date": forms.HiddenInput(),
            "transaction_type": forms.HiddenInput(),
            "in_mrs": forms.HiddenInput(),
        }


class ReportSearchForm(forms.Form):

    REPORT_CHOICES = [
        # (1, "Branch Summary"),
        (2, "RC Summary"),
        (3, "Project Summary"),
    ]
    REPORT_CHOICES.insert(0, (None, "------"))

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)

    def __init__(self, *args, **kwargs):
        super.__init__(self, *args, **kwargs)

        fy_choices = [(obj.id, "{}".format(obj.full)) for obj in shared_models.FiscalYear.objects.all()]
        fy_choices.insert(0, (None, "------"))

        rc_choices = [(obj.id, obj) for obj in shared_models.ResponsibilityCenter.objects.all()]
        rc_choices.insert(0, (None, "------"))

        project_choices = [(obj.id, "{} - {}".format(obj.code, obj.name)) for obj in shared_models.Project.objects.all()]
        project_choices.insert(0, (None, "------"))

        self.fields['fiscal_year'].choices = fy_choices
        self.fields['fiscal_year'].required = True

        self.fields['rc'].choices = rc_choices
        self.fields['rc'].required = False

        self.fields['project'].choices = project_choices
        self.fields['project'].required = False
        self.fields['project'].label = "Project"
