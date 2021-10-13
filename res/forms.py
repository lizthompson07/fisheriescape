from django import forms
from django.forms import modelformset_factory

from . import models

attr_fp_date_time = {"class": "fp-date-time-with-seconds", "placeholder": "Select Date and Time.."}
chosen_js = {"class": "chosen-select-contains"}
YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class ContextForm(forms.ModelForm):
    class Meta:
        model = models.Context
        fields = "__all__"


ContextFormset = modelformset_factory(
    model=models.Context,
    form=ContextForm,
    extra=1,
)


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = models.Outcome
        fields = "__all__"


OutcomeFormset = modelformset_factory(
    model=models.Outcome,
    form=OutcomeForm,
    extra=1,
)


class AchievementCategoryForm(forms.ModelForm):
    class Meta:
        model = models.AchievementCategory
        fields = "__all__"


AchievementCategoryFormset = modelformset_factory(
    model=models.AchievementCategory,
    form=AchievementCategoryForm,
    extra=1,
)


class GroupLevelForm(forms.ModelForm):
    class Meta:
        model = models.GroupLevel
        fields = "__all__"


GroupLevelFormset = modelformset_factory(
    model=models.GroupLevel,
    form=GroupLevelForm,
    extra=1,
)


class PublicationTypeForm(forms.ModelForm):
    class Meta:
        model = models.PublicationType
        fields = "__all__"


PublicationTypeFormset = modelformset_factory(
    model=models.PublicationType,
    form=PublicationTypeForm,
    extra=1,
)



class ApplicationForm(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = "__all__"
