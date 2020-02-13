from django import forms
from . import models

class ItemForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = "__all__"