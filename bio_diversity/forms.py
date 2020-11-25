from django import forms
from bio_diversity import models


class InstForm(forms.ModelForm):
    class Meta:
        model = models.InstDetCode
        exclude = []
        widgets = {
        }

