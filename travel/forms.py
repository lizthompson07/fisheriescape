from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User as AuthUser
from projects import models as projects_models

from . import models

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = ["total_cost", ]

        widgets = {
            'start_date': forms.DateInput(attrs={"type": "date"}),
            'end_date': forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        AuthUser.objects.all().order_by("last_name", "first_name")]
        USER_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = AuthUser.objects.all().order_by("last_name", "first_name")
        self.fields['user'].choices = USER_CHOICES


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "------"),
        (1, "CFTS export (xlsx)"),
        (2, "Print Travel Plan PDF"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    # report #1
    fiscal_year = forms.ChoiceField(required=False, label=_('Fiscal year'))
    # report #2
    traveller = forms.ChoiceField(required=False, label=_('Fiscal year'))

    def __init__(self, *args, **kwargs):
        FY_CHOICES = [(fy.id, str(fy)) for fy in projects_models.FiscalYear.objects.all().order_by("id")]
        TRAVELLER_CHOICES = [(e['email'], "{}, {}".format(e['last_name'], e['first_name'])) for e in
                             models.Event.objects.values("email", "first_name", "last_name").order_by("last_name", "first_name").distinct()]
        super().__init__(*args, **kwargs)
        self.fields['fiscal_year'].choices = FY_CHOICES
        self.fields['traveller'].choices = TRAVELLER_CHOICES
