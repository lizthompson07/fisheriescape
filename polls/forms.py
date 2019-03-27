from django import forms
from django.utils.translation import gettext as _
from . import models
from django.contrib.auth.models import User
from shared_models import models as shared_models


class NewInstrumentForm(forms.ModelForm):
    class Meta:
        model = models.Instrument
        fields = [
            'purchase_date',
            'project_title',
            # 'section',
            # 'last_modified_by',
        ]
        widgets = {
            # 'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 5}),
        }


class InstrumentSubmitForm(forms.ModelForm):
    class Meta:
        model = models.Instrument
        fields = [
            # 'last_modified_by',
            'submitted',
        ]
        widgets = {
            # 'last_modified_by': forms.HiddenInput(),
            'submitted': forms.HiddenInput(),
        }


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = models.Instrument
        exclude = [
            'submitted',
            'date_last_modified',
            # 'section_head_approved',
            # 'description_html',
            # 'priorities_html',
            # 'deliverables_html',
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={"type": "date"}),
            # 'end_date': forms.DateInput(attrs={"type": "date"}),
            # 'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 5}),
            # "description": forms.Textarea(attrs={"rows": 8}),
            # "notes": forms.Textarea(attrs={"rows": 5}),
        }
