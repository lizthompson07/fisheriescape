from django import forms
from . import models

chosen_js = {"class": "chosen-select-contains"}
multi_select_js = {"class": "multi-select"}

class ItemForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = "__all__"
        widgets = {
            'container': forms.CheckboxInput(),
            'suppliers': forms.SelectMultiple(attrs=chosen_js),
            # 'suppliers': forms.SelectMultiple(attrs=multi_select_js),
        }

class QuantityForm(forms.ModelForm):
    class Meta:
        model = models.Quantity
        fields = "__all__"


class QuantityForm1(forms.ModelForm):
    class Meta:
        model = models.Quantity
        fields = "__all__"
        widgets = {
            'item': forms.HiddenInput(),
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = models.Location
        fields = "__all__"


class PersonnelForm(forms.ModelForm):
    class Meta:
        model = models.Personnel
        fields = "__all__"

class SupplierForm(forms.ModelForm):
    class Meta:
        model = models.Supplier
        fields = "__all__"

class SupplierForm1(forms.ModelForm):
    class Meta:
        model = models.Supplier
        fields = "__all__"
        widgets = {
            'item': forms.HiddenInput(),
        }

class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"
        widgets = {
            'item': forms.HiddenInput(),
        }

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

class ReportGeneratorForm(forms.Form):
    report = forms.ChoiceField(required=True)
    container = forms.ChoiceField(required=True)
    location = forms.ChoiceField(required=False, label="Location/Container Name", widget=forms.Select(attrs=chosen_js))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        report_choices = [
            (1, "Container Summary"),

        ]
        report_choices.insert(0, (None, "------"))

        container_choices = [(obj.id, "{}".format(obj.container)) for obj in models.Location.objects.all()]
        container_choices.insert(0, (None, "------"))

        location_choices = [(obj.id, "{}".format(obj.location)) for obj in models.Location.objects.all()]
        location_choices.insert(0, (None, "------"))

        self.fields['report'].choices = report_choices
        self.fields['container'].choices = container_choices
        self.fields['location'].choices = location_choices
