from django import forms
from django.core import validators
from django.utils import timezone

from . import models
from django.contrib.auth.models import User


class EntryCreateForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        exclude = [
            'date_last_modified',
            'date_created',
        ]
        widgets = {
            'initial_date': forms.DateInput(attrs={"type": "date"}),
            'last_modified_by': forms.HiddenInput(),
            'created_by': forms.HiddenInput(),
        }


class EntryForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        exclude = [
            'date_last_modified',
            'date_created',
            'created_by',
        ]
        widgets = {
            'initial_date': forms.DateInput(attrs={"type": "date"}),
            'last_modified_by': forms.HiddenInput(),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = models.EntryNote
        fields = "__all__"
        widgets = {
            'entry': forms.HiddenInput(),
            'author': forms.HiddenInput(),
        }


class ReportSearchForm(forms.Form):
    FY_CHOICES = [
        ("{}".format(y["fiscal_year"]), "{}".format(y["fiscal_year"])) for y in
        models.Entry.objects.all().values("fiscal_year").order_by("fiscal_year").distinct() if y is not None]
    FY_CHOICES.insert(0, (None, "all years"))
    ORG_CHOICES = [(obj.id, obj) for obj in models.Organization.objects.all()]

    REPORT_CHOICES = (
        (None, "------"),
        (1, "Capacity Report (Excel Spreadsheet)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    fiscal_year = forms.ChoiceField(required=False, choices=FY_CHOICES, label='Fiscal year')
    organizations = forms.MultipleChoiceField(required=False, choices=ORG_CHOICES,
                                              label='Organizations (Leave blank for all)')

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = "__all__"