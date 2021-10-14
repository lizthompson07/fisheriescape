from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy

from shared_models.models import Section
from . import models

attr_fp_date_range = {"class": "fp-date-range", "placeholder": gettext_lazy("Click to select a range of dates..")}
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
    date_range = forms.CharField(widget=forms.TextInput(attrs=attr_fp_date_range), label=gettext_lazy("Period covered by this application"), required=True)

    class Meta:
        model = models.Application
        fields = [
            "applicant",
            "manager",
            "current_group_level",
            "target_group_level",
            "section",
        ]
        widgets = {
            'applicant': forms.Select(attrs=chosen_js),
            'section': forms.Select(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        section_choices = [(obj.id, obj.full_name) for obj in Section.objects.all()]
        section_choices.insert(0, (None, "------"))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = section_choices



class ApplicationTimestampUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = [
            "work_location",
        ]
        widgets = {
            "work_location": forms.HiddenInput()
        }

