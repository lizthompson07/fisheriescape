from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy, gettext as _

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


class ReviewTypeForm(forms.ModelForm):
    class Meta:
        model = models.ReviewType
        fields = "__all__"


ReviewTypeFormset = modelformset_factory(
    model=models.ReviewType,
    form=ReviewTypeForm,
    extra=1,
)


class SiteSectionForm(forms.ModelForm):
    class Meta:
        model = models.SiteSection
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description_en'].widget.attrs = dict(rows=10)
        self.fields['description_fr'].widget.attrs = dict(rows=10)


SiteSectionFormset = modelformset_factory(
    model=models.SiteSection,
    form=SiteSectionForm,
    extra=1,
)


class ApplicationForm(forms.ModelForm):
    # date_range = forms.CharField(widget=forms.TextInput(attrs=attr_fp_date_range), label=gettext_lazy("Period covered by this application"), required=True)

    class Meta:
        model = models.Application
        fields = [
            "applicant",
            "manager",
            "current_group_level",
            "target_group_level",
            "section",
            "application_start_date",
            "application_end_date",
        ]
        widgets = {
            'applicant': forms.Select(attrs=chosen_js),
            'manager': forms.Select(attrs=chosen_js),
            'section': forms.Select(attrs=chosen_js),
            'application_start_date': forms.DateTimeInput(attrs=dict(type="date")),
            'application_end_date': forms.DateTimeInput(attrs=dict(type="date")),
        }

    def __init__(self, *args, **kwargs):
        section_choices = [(obj.id, obj.full_name) for obj in Section.objects.filter(division__branch__sector__name__icontains="science")]
        section_choices.insert(0, (None, "------"))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = section_choices

    def clean(self):
        """
        - make sure that application end date is after application start date
        """
        cleaned_data = super().clean()
        application_start_date = cleaned_data.get("application_start_date")
        application_end_date = cleaned_data.get("application_end_date")
        if application_end_date < application_start_date:
            msg = _('The application end date must be after the application start date')
            self.add_error('end_date', msg)
        return self.cleaned_data


class ApplicationTimestampUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = [
            "work_location",
        ]
        widgets = {
            "work_location": forms.HiddenInput()
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = models.Achievement
        exclude = ("user",)
