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
    class Meta:
        model = models.Transaction
        exclude = ["fiscal_year", "outstanding_obligation"]
        widgets = {
            "created_by": forms.HiddenInput(),
            "requisition_date": forms.DateInput(attrs={"type": "date"}),
            "invoice_date": forms.DateInput(attrs={"type": "date"})
        }


class ReportSearchForm(forms.Form):
    FY_CHOICES = [("{}-{}".format(y, y + 1), "{}-{}".format(y, y + 1)) for y in
                  range(timezone.now().year - 2, timezone.now().year + 1)]
    RC_CHOICES = [(obj.id, obj) for obj in models.ResponsibilityCenter.objects.all()]
    RC_CHOICES.insert(0, (None, "------"))

    REPORT_CHOICES = [
        (1, "Branch Summary"),
        (2, "Account Summary"),
        (3, "Project Summary"),
    ]
    REPORT_CHOICES.insert(0, (None, "------"))

    fiscal_year = forms.ChoiceField(required=True, choices=FY_CHOICES)
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    rc = forms.ChoiceField(required=False, choices=RC_CHOICES, label="Responsibility centre")
