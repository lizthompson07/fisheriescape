from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _
from shared_models import models as shared_models
from . import models
from django.utils.safestring import mark_safe


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
            'date_last_modified': forms.HiddenInput(),
        }
        help_texts = {
            'organization_type': 'its a mighty <br> cheese pizza',
            'address': 'where ya live'
        }

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})



class PersonForm(forms.ModelForm):

    organization = forms.ModelMultipleChoiceField(queryset=models.Organization.objects.all(), widget=forms.SelectMultiple(attrs=attr_chosen_contains))

    class Meta:
        model = models.Person #ml
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})

class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = models.Objective
        fields = '__all__'
        widgets = {
            'outcomes_deadline': forms.DateInput(attrs={"type": "date"}),
            'pst_req': forms.Select(choices=YES_NO_CHOICES),
            'sil_req': forms.Select(choices=YES_NO_CHOICES),
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ObjectiveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})

class MethodForm(forms.ModelForm):
    class Meta:
        model = models.Method
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(MethodForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})

class DatabasesUsedForm(forms.ModelForm):
    class Meta:
        model = models.DatabasesUsed
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(DatabasesUsedForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Feedback
        fields = '__all__'
        widgets = {
            'sent_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})

class MeetingsForm(forms.ModelForm):
    class Meta:
        model = models.Meetings
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(MeetingsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})

class ReportsForm(forms.ModelForm):
    class Meta:
        model = models.Reports
        fields = '__all__'
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ReportsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'top',
                     'data-container': 'body', 'data-html': "true"})