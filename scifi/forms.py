from django import forms
from django.utils import timezone

from . import models


class ResponsibilityCentreForm(forms.ModelForm):
    class Meta:
        model = models.ResponsibilityCenter
        fields = "__all__"


class LineObjectForm(forms.ModelForm):
    class Meta:
        model = models.LineObject
        fields = "__all__"


class BusinessLineForm(forms.ModelForm):
    class Meta:
        model = models.BusinessLine
        fields = "__all__"


class AllotmentCodeForm(forms.ModelForm):
    class Meta:
        model = models.AllotmentCode
        fields = "__all__"


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = "__all__"


class TransactionForm(forms.ModelForm):
    do_another = forms.IntegerField(required=False, widget=forms.HiddenInput())
    class Meta:
        model = models.Transaction
        exclude = ["fiscal_year", "outstanding_obligation"]
        widgets = {
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
    # FY_CHOICES = [("{}-{}".format(y, y + 1), "{}-{}".format(y, y + 1)) for y in
    #               range(timezone.now().year - 2, timezone.now().year + 1)]
    # RC_CHOICES = [(obj.id, obj) for obj in models.ResponsibilityCenter.objects.all()]
    # RC_CHOICES.insert(0, (None, "------"))
    # PROJECT_CHOICES = [(obj.id, "{} - {}".format(obj.code, obj.name)) for obj in models.Project.objects.all()]
    # PROJECT_CHOICES.insert(0, (None, "------"))
    # REPORT_CHOICES = [
    #     (1, "Branch Summary"),
    #     (2, "RC Summary"),
    #     (3, "Project Summary"),
    # ]
    # REPORT_CHOICES.insert(0, (None, "------"))
    #
    # report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    # fiscal_year = forms.ChoiceField(required=True, choices=FY_CHOICES)
    # rc = forms.ChoiceField(required=False, choices=RC_CHOICES, label="Responsibility centre")
    # project = forms.ChoiceField(required=False, choices=PROJECT_CHOICES, label="Project")
    pass