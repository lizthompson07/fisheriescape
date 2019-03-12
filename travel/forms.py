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
            'conf_start_date': forms.DateInput(attrs={"type": "date"}),
            'conf_end_date': forms.DateInput(attrs={"type": "date"}),
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
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    # report #1
    fiscal_year = forms.ChoiceField(required=False, label=_('Fiscal year'))

    def __init__(self, *args, **kwargs):
        FY_CHOICES = [(fy.id, str(fy)) for fy in projects_models.FiscalYear.objects.all().order_by("id")]
        super().__init__(*args, **kwargs)
        self.fields['fiscal_year'].choices = FY_CHOICES

