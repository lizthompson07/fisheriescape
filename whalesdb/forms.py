from django import forms
from whalesdb import models


class CodeEditForm(forms.ModelForm):

    value = forms.CharField(max_length=255, label="")

    class Meta:
        model = models.EqaAdcBitsCode
        fields = ['value']
