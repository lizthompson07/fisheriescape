from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext as _
from shared_models import models as shared_models
from . import models

attr_chosen_contains = {"class": "chosen-select-contains"}
attr_chosen = {"class": "chosen-select"}
attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}
attr_fp_date_time = {"class": "fp-date-time", "placeholder": "Select Date and Time.."}
attr_fp_date_time_email = {"class": "fp-date-time green-borders", "placeholder": "Select Date and Time.."}

multi_select_js = {"class": "multi-select"}
class_editable = {"class": "editable"}

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization #ml
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = models.Person #ml
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = models.Objective
        fields = '__all__'
        widgets = {
            'outcomes_deadline': forms.DateInput(attrs={"type": "date"}),
            'pst_req': forms.Select(choices=YES_NO_CHOICES),
            'sil_req': forms.Select(choices=YES_NO_CHOICES),
            'last_modified_by': forms.HiddenInput(),
        }


class MethodForm(forms.ModelForm):
    class Meta:
        model = models.Method
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class DatabasesUsedForm(forms.ModelForm):
    class Meta:
        model = models.DatabasesUsed
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Feedback
        fields = '__all__'
        widgets = {
            'sent_by': forms.HiddenInput(),
        }


class MeetingsForm(forms.ModelForm):
    class Meta:
        model = models.Meetings
        fields = '__all__'


class ReportsForm(forms.ModelForm):
    class Meta:
        model = models.Reports
        fields = '__all__'
