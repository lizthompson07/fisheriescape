from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from . import models

chosen_js_sw = {"class": "chosen-select"}
chosen_js = {"class": "chosen-select-contains"}
multi_select_js = {"class": "multi-select"}


class AppForm(forms.ModelForm):
    class Meta:
        model = models.App
        fields = "__all__"
        widgets = {
            "owner": forms.HiddenInput(),
        }
