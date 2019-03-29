from django import forms
from django.utils.translation import gettext as _
from . import models
from django.contrib.auth.models import User
from shared_models import models as shared_models


class NewInstrumentForm(forms.ModelForm):

    class Meta:
        # TYPE_CHOICES = [('CTD', 'CTD'), ('ADCP', 'ADCP')]
        model = models.Instrument
        fields = [
            'instrument_type',
            'serial_number',
            'purchase_date',
            'date_of_last_service',
            'date_of_next_service',
            'project_title',
            # 'last_modified_by',
        ]
        widgets = {
            # 'last_modified_by': forms.HiddenInput(),
            # 'purchase_date': forms.DateInput( attrs={"type": "date",'placeholder':'2015-01-01'}),
            # 'instrument_type': forms.Textarea(attrs={"rows": 1},  choices=TYPE_CHOICES),
            # 'instrument_type': forms.Select(choices=TYPE_CHOICES),
            # 'serial_number': forms.Textarea(attrs={"rows": 1}),
            # 'date_of_last_service': forms.DateInput( attrs={"type": "date",'placeholder':'2015-01-01'}),
            # 'date_of_next_service': forms.DateInput(attrs={"type": "date", 'placeholder': '2015-01-01'}),
            # 'end_date': forms.DateInput(attrs={"type": "date"}),
            # 'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 1}),
            # "description": forms.Textarea(attrs={"rows": 8}),
            # "notes": forms.Textarea(attrs={"rows": 5}),
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
        #     # 'last_modified_by': forms.HiddenInput(),
        #     'purchase_date': forms.DateInput( attrs={"type": "date",'placeholder':'2015-01-01'}),
        #     # 'instrument_type': forms.Textarea(attrs={"rows": 1},  choices=TYPE_CHOICES),
        #     # 'instrument_type': forms.Select(choices=TYPE_CHOICES),
        #     'serial_number': forms.Textarea(attrs={"rows": 1}),
        #     'date_of_last_service': forms.DateInput( attrs={"type": "date",'placeholder':'2015-01-01'}),
        #     'date_of_next_service': forms.DateInput(attrs={"type": "date", 'placeholder': '2015-01-01'}),
        #     # 'end_date': forms.DateInput(attrs={"type": "date"}),
        #     # 'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 1}),
        #     # "description": forms.Textarea(attrs={"rows": 8}),
        #     # "notes": forms.Textarea(attrs={"rows": 5}),
        }


class DeploymentForm(forms.ModelForm):
    class Meta:
        model = models.Deployment
        exclude = [
            'submitted',
            'date_last_modified',

        ]

        widgets = {
            'mooring': forms.Textarea(attrs={"rows": 1}),
            'mooring_number': forms.Textarea(attrs={"rows": 1}),
            'depth': forms.Textarea(attrs={"rows": 1}),
            'lat': forms.Textarea(attrs={"rows": 1}),
            'lon': forms.Textarea(attrs={"rows": 1}),
            'description': forms.Textarea(attrs={"rows": 1}),
        #     # "description": forms.Textarea(attrs={"rows": 8}),
        #     # "notes": forms.Textarea(attrs={"rows": 5}),
        }
