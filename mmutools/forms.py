from django import forms
from . import models

class ItemForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = "__all__"
        widgets = {
            'container': forms.CheckboxInput,
        }

class QuantityForm(forms.ModelForm):
    class Meta:
        model = models.Quantity
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('initial') and kwargs.get('initial').get('item'):
            self.fields.get('item').widget = forms.HiddenInput()

class PersonnelForm(forms.ModelForm):
    class Meta:
        model = models.Personnel
        fields = "__all__"

class SupplierForm(forms.ModelForm):
    class Meta:
        model = models.Supplier
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('initial') and kwargs.get('initial').get('item'):
            self.fields.get('item').widget = forms.HiddenInput()

class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"

class LendingForm(forms.ModelForm):
    class Meta:
        model = models.Lending
        fields = "__all__"

class IncidentForm(forms.ModelForm):
    class Meta:
        model = models.Incident
        fields = "__all__"
        widgets = {
            'submitted': forms.CheckboxInput,
            'gear_presence': forms.CheckboxInput,
            'exam': forms.CheckboxInput,
            'necropsy': forms.CheckboxInput,
            'photos': forms.CheckboxInput,
        }