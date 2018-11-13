from django import forms
from . import models


class BugCreateForm(forms.ModelForm):
    class Meta:
        model = models.Bug
        exclude = ['date_resolved', 'resolved']
        widgets = {
            'user':forms.HiddenInput(),
            'detail':forms.Textarea(attrs={'rows':'5'})
        }

class BugUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Bug
        exclude = ['resolved']
        widgets = {
            'date_resolved':forms.DateInput(attrs={'type': 'date'}),
            'user':forms.HiddenInput(),
            'detail':forms.Textarea(attrs={'rows':'5'})
            
        }
