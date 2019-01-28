from django import forms
from . import models

class ResponsibilityCentreForm(forms.ModelForm):
    class Meta:
        model = models.ResponsibilityCenter
        fields = "__all__"


class LineObjectForm(forms.ModelForm):
    class Meta:
        model = models.LineObject
        fields = "__all__"


class BusinessLineForm(forms.ModelForm):
    class Meta:
        model = models.BusinessLine
        fields = "__all__"


class AllotmentCodeForm(forms.ModelForm):
    class Meta:
        model = models.AllotmentCode
        fields = "__all__"


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = "__all__"