from django import forms
from django.core import validators
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

