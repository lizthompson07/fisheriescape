from django import forms
from bio_diversity import models


class InstdcForm(forms.ModelForm):
    class Meta:
        model = models.InstDetCode
        exclude = []
        widgets = {
        }

