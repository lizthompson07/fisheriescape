from django import forms
from django.utils.translation import gettext as _
from . import models
from django.contrib.auth.models import User
from shared_models import models as shared_models
from django.utils import timezone
from datetime import date, timedelta, datetime


class NewInstrumentForm(forms.ModelForm):
    purchase_date = forms.DateField(input_formats=["%Y-%b-%d"],
                                    widget=forms.DateInput(format="%Y-%b-%d", attrs={"type": "datepicker",
                                                   "value": timezone.now().strftime("%Y-%b-%d")}))
    date_of_last_service = forms.DateField(input_formats=["%Y-%b-%d"],
                                    widget=forms.DateInput(format="%Y-%b-%d", attrs={"type": "datepicker",
                                                   "value": timezone.now().strftime("%Y-%b-%d")}))
    date_of_next_service = forms.DateField(input_formats=["%Y-%b-%d"],
                                    widget=forms.DateInput(format="%Y-%b-%d", attrs={"type": "datepicker",
                                                   "value": (timezone.now()+ timedelta(days=365)).strftime("%Y-%b-%d")}))

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
            # 'purchase_date' : forms.DateInput(attrs={"type": "datepicker",
            #                                        "value": timezone.now().strftime("%Y-%b-%d")},
            #                                 ),
            # 'instrument_type': forms.Textarea(attrs={"rows": 1},  choices=TYPE_CHOICES),
            # 'instrument_type': forms.Select(choices=TYPE_CHOICES),
            # 'serial_number': forms.Textarea(attrs={"rows": 1}),
            # 'date_of_last_service': forms.DateInput(attrs={"type": "date",
            #                                                "value": timezone.now().strftime("%Y-%b-%d")}),
            # 'date_of_next_service': forms.DateInput(attrs={"type": "date",
            #                                                "value": (timezone.now() + timedelta(days=365)).strftime("%Y-%b-%d")}),
            # 'end_date': forms.DateInput(attrs={"type": "date"}),
            # 'last_modified_by': forms.HiddenInput(),
            'project_title': forms.Textarea(attrs={"rows": 1}),
            'scientist': forms.Textarea(attrs={"rows": 1}),
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
    # purchase_date = forms.DateField(input_formats=["%Y-%b-%d"])
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
        #     'date_of_last_service': forms.DateInput( attrs={"type": "date",
        #                                                     'value': timezone.now().strftime("%Y-%b-%d")}),
        #     'date_of_next_service': forms.DateInput(attrs={"type": "date",
        #                                                    'value': (timezone.now()+ timedelta(days=365)).strftime("%Y-%b-%d")}),
        #     # 'end_date': forms.DateInput(attrs={"type": "date"}),
        #     # 'last_modified_by': forms.HiddenInput(),
            'scientist': forms.Textarea(attrs={"rows": 1}),
            'project_title': forms.Textarea(attrs={"rows": 1}),
        #     # "description": forms.Textarea(attrs={"rows": 8}),
        #     # "notes": forms.Textarea(attrs={"rows": 5}),
        }


class MooringForm(forms.ModelForm):
    class Meta:
        model = models.Mooring
        exclude = [
            'submitted',
            'date_last_modified',

        ]

        widgets = {
            # 'instrument': forms.HiddenInput(),
            'instruments': forms.HiddenInput(),
            # 'mooring': forms.Textarea(attrs={"rows": 1}),
            # 'mooring_number': forms.Textarea(attrs={"rows": 1}),
            # 'deploy_time': forms.DateTimeInput(attrs={"type": "date",
            #                                     'input_formats': ['%Y-%m-%d %H:%M:%S'],
            #                                                'placeholder': (timezone.now()+ timedelta(days=365)).strftime("%Y-%b-%d")}),
            # 'recover_time': forms.DateTimeInput(attrs={"type": "date",
            #                                                'value': (timezone.now() + timedelta(days=365)).strftime(
            #                                                    "%Y-%b-%d %T")}),
            'depth': forms.Textarea(attrs={"rows": 1}),
            'lat': forms.Textarea(attrs={"rows": 1}),
            'lon': forms.Textarea(attrs={"rows": 1}),
            'comments': forms.Textarea(attrs={"rows": 2}),
        #     # "description": forms.Textarea(attrs={"rows": 8}),
        #     # "notes": forms.Textarea(attrs={"rows": 5}),
        }


# class AddDeploymentForm(forms.ModelForm):
#     class Meta:
#         model = models.Mooring
#         exclude = [
#             'submitted',
#             'date_last_modified',
#
#         ]
#
#         widgets = {
#             # 'instrument': forms.HiddenInput(),
#             # 'instruments': forms.HiddenInput(),
#             'mooring': forms.HiddenInput(),
#             'mooring_number': forms.HiddenInput(),
#             'deploy_time': forms.DateTimeInput(attrs={"type": "date",
#                                                 'input_formats': ['%Y-%m-%d %H:%M:%S'],
#                                                            'placeholder': (timezone.now()+ timedelta(days=365)).strftime("%Y-%b-%d")}),
#             'recover_time': forms.DateTimeInput(attrs={"type": "date",
#                                                            'value': (timezone.now() + timedelta(days=365)).strftime(
#                                                                "%Y-%b-%d %T")}),
#             'depth': forms.Textarea(attrs={"rows": 1}),
#             'lat': forms.Textarea(attrs={"rows": 1}),
#             'lon': forms.Textarea(attrs={"rows": 1}),
#             'comments': forms.Textarea(attrs={"rows": 2}),
#         #     # "description": forms.Textarea(attrs={"rows": 8}),
#         #     # "notes": forms.Textarea(attrs={"rows": 5}),
#         }


class AddInstrumentToMooringForm(forms.ModelForm):
    class Meta:
        model = models.InstrumentMooring
        exclude = [
            'submitted',
            'date_last_modified',

        ]

        widgets = {
            'mooring': forms.HiddenInput(),
            'depth': forms.Textarea(attrs={"rows": 1}),
            'lat': forms.Textarea(attrs={"rows": 1}),
            'lon': forms.Textarea(attrs={"rows": 1}),
            'comments': forms.Textarea(attrs={"rows": 2}),
        #     # "description": forms.Textarea(attrs={"rows": 8}),
        #     # "notes": forms.Textarea(attrs={"rows": 5}),
        }


class AddMooringToInstrumentForm(forms.ModelForm):
    class Meta:
        model = models.InstrumentMooring
        exclude = [
            'submitted',
            'date_last_modified',

        ]

        widgets = {
            'instrument': forms.HiddenInput(),
            'depth': forms.Textarea(attrs={"rows": 1}),
            'lat': forms.Textarea(attrs={"rows": 1}),
            'lon': forms.Textarea(attrs={"rows": 1}),
            'comments': forms.Textarea(attrs={"rows": 2}),
        #     # "description": forms.Textarea(attrs={"rows": 8}),
        #     # "notes": forms.Textarea(attrs={"rows": 5}),
        }


class EditInstrumentMooringForm(forms.ModelForm):
    class Meta:
        model = models.InstrumentMooring
        exclude = [
            'submitted',
            'date_last_modified',

        ]

        widgets = {
            # 'instrument': forms.HiddenInput(),
            # 'instruments': forms.HiddenInput(),
            # 'deployment': forms.HiddenInput(),
            # 'mooring': forms.HiddenInput(),
            # 'mooring_number': forms.HiddenInput(),
            # 'deploy_time': forms.DateTimeInput(attrs={"type": "date",
            #                                     'input_formats': ['%Y-%m-%d %H:%M:%S'],
            #                                                'placeholder': (timezone.now()+ timedelta(days=365)).strftime("%Y-%b-%d")}),
            # 'recover_time': forms.DateTimeInput(attrs={"type": "date",
            #                                                'value': (timezone.now() + timedelta(days=365)).strftime(
            #                                                    "%Y-%b-%d %T")}),
            'depth': forms.Textarea(attrs={"rows": 1}),
            'lat': forms.Textarea(attrs={"rows": 1}),
            'lon': forms.Textarea(attrs={"rows": 1}),
            'comments': forms.Textarea(attrs={"rows": 2}),
        #     # "description": forms.Textarea(attrs={"rows": 8}),
        #     # "notes": forms.Textarea(attrs={"rows": 5}),
        }


class MooringSubmitForm(forms.ModelForm):
    class Meta:
        model = models.Mooring
        fields = [
            # 'last_modified_by',
            'submitted',
        ]
        widgets = {
            # 'last_modified_by': forms.HiddenInput(),
            'submitted': forms.HiddenInput(),
        }


