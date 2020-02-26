from django import forms
from django.forms import modelformset_factory
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import User as AuthUser
from shared_models import models as shared_models

from . import models

chosen_js = {"class": "chosen-select-contains"}
attr_fp_date = {"class": "fp-date", "placeholder": "Click to select a date.."}
attr_phone = {"class": "input-phone"}
attr_row3 = {"rows": 3}
attr_row4 = {"rows": 4}

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class ReviewerApprovalForm(forms.ModelForm):
    approved = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    changes_requested = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    stay_on_page = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.Reviewer
        fields = [
            "comments",
        ]
        labels = {
            "comments": _("Please provide your comments here...")
        }
        widgets = {
            "comments": forms.Textarea(attrs=attr_row3)
        }


class ReviewerSkipForm(forms.ModelForm):
    class Meta:
        model = models.Reviewer
        fields = [
            "comments",
        ]
        labels = {
            "comments": _("If so, please provide the rationale here...")
        }
        widgets = {
            "comments": forms.Textarea(attrs=attr_row3)
        }


class TripRequestApprovalForm(forms.Form):
    approved = forms.BooleanField(widget=forms.HiddenInput(), required=False)


class TripRequestForm(forms.ModelForm):
    stay_on_page = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.TripRequest
        exclude = [
            "total_cost",
            "fiscal_year",
            "submitted",
            "status",
            "exclude_from_travel_plan",
            "admin_notes",
        ]
        labels = {
            'bta_attendees': _("Other attendees covered under BTA (i.e., they will not need to have a travel plan)"),
        }

        widgets = {
            'bta_attendees': forms.SelectMultiple(attrs=chosen_js),
            'trip': forms.Select(attrs=chosen_js),
            'is_group_request': forms.Select(choices=YES_NO_CHOICES),
            'objective_of_event': forms.Textarea(attrs=attr_row3),
            'benefit_to_dfo': forms.Textarea(attrs=attr_row3),
            'multiple_attendee_rationale': forms.Textarea(attrs=attr_row3),
            'late_justification': forms.Textarea(attrs=attr_row3),
            'funding_source': forms.Textarea(attrs=attr_row3),
            'notes': forms.Textarea(attrs=attr_row3),

            # hidden fields
            'parent_request': forms.HiddenInput(),

            # non-group trip request fields

            # user fields
            'is_public_servant': forms.Select(attrs={"class": "not-a-group-field disappear-if-user"}, choices=YES_NO_CHOICES),
            'user': forms.Select(attrs={"class": "chosen-select-contains"}),
            'first_name': forms.TextInput(attrs={"class": "not-a-group-field disappear-if-user"}),
            'last_name': forms.TextInput(attrs={"class": "not-a-group-field disappear-if-user"}),
            'section': forms.Select(attrs=chosen_js),
            'email': forms.EmailInput(attrs={"class": "not-a-group-field disappear-if-user"}),
            'address': forms.TextInput(attrs={"class": "not-a-group-field"}),
            'phone': forms.TextInput(attrs={"class": "not-a-group-field input-phone"}),
            'company_name': forms.TextInput(attrs={"class": "not-a-group-field disappear-if-user hide-if-public-servant"}),
            'is_research_scientist': forms.Select(attrs={"class": "not-a-group-field hide-if-not-public-servant"}, choices=YES_NO_CHOICES),

            'start_date': forms.DateInput(attrs={"class": "not-a-group-field fp-date", "placeholder": "Click to select a date.."}),
            'end_date': forms.DateInput(attrs={"class": "not-a-group-field fp-date", "placeholder": "Click to select a date.."}),
            'departure_location': forms.TextInput(attrs={"class": "not-a-group-field"}),
            'role': forms.Select(attrs={"class": "not-a-group-field"}),
            'region': forms.Select(attrs={"class": "not-a-group-field hide-if-not-public-servant"}),
            'role_of_participant': forms.Textarea(attrs={"class": "not-a-group-field"}),
            'multiple_conferences_rationale': forms.Textarea(attrs={"class": "not-a-group-field"}),
        }

    def __init__(self, *args, **kwargs):
        user_choices = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        AuthUser.objects.all().order_by("last_name", "first_name")]
        user_choices.insert(0, tuple((None, "---")))

        section_heads = [section.head for section in shared_models.Section.objects.filter(head__isnull=False)]
        division_heads = [division.head for division in shared_models.Division.objects.filter(head__isnull=False)]
        branch_heads = [branch.head for branch in shared_models.Branch.objects.filter(head__isnull=False)]
        region_heads = [region.head for region in shared_models.Region.objects.filter(head__isnull=False)]

        heads = list()
        heads.extend(section_heads)
        heads.extend(division_heads)
        heads.extend(branch_heads)
        heads.extend(region_heads)
        # manually add Arran McPherson
        heads.append(AuthUser.objects.get(email__iexact="Arran.McPherson@dfo-mpo.gc.ca"))
        heads = set(heads)

        recommender_chocies = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                               AuthUser.objects.all().order_by("last_name", "first_name") if u in heads]
        recommender_chocies.insert(0, tuple((None, "---")))

        section_choices = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.filter(division__branch_id__in=[1, 3, 9, ]).order_by("division__branch__region",
                                                                                                           "division__branch",
                                                                                                           "division", "name")]
        section_choices.insert(0, tuple((None, "---")))

        trip_choices = [(t.id, str(t)) for t in models.Conference.objects.filter(start_date__gte=timezone.now())]
        trip_choices.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['trip'].choices = trip_choices
        self.fields['user'].choices = user_choices
        self.fields['bta_attendees'].choices = user_choices
        self.fields['section'].choices = section_choices

        # general trip infomation
        field_list = [
            'is_group_request',
            'purpose',
            'reason',
            'trip',
            'departure_location',
            'destination',
            'start_date',
            'end_date',
            'bta_attendees',
            'non_dfo_costs',
            'non_dfo_org',
        ]
        for field in field_list:
            self.fields[field].group = 1

        # traveller info
        field_list = [
            'user',
            'section',
            'first_name',
            'last_name',
            'address',
            'phone',
            'email',
            'is_public_servant',
            'is_research_scientist',
            'company_name',
            'region',
        ]
        for field in field_list:
            self.fields[field].group = 2

        # justification
        field_list = [
            'role',
            'role_of_participant',
            'objective_of_event',
            'benefit_to_dfo',
            'multiple_conferences_rationale',
            'multiple_attendee_rationale',
            'late_justification',
            'funding_source',
            'notes',
        ]
        for field in field_list:
            self.fields[field].group = 3

        # are there any forgotten fields?
        for field in self.fields:
            try:
                self.fields[field].group
            except AttributeError:
                print(f'Adding label: "Unspecified" to field "{field}".')
                self.fields[field].group = 0


class TripRequestAdminNotesForm(forms.ModelForm):
    class Meta:
        model = models.TripRequest
        fields = [
            "admin_notes",
        ]


class ChildTripRequestForm(forms.ModelForm):
    stay_on_page = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.TripRequest
        fields = [
            'user',
            'first_name',
            'last_name',
            'address',
            'phone',
            'email',
            'is_public_servant',
            'is_research_scientist',
            'company_name',
            'region',
            'start_date',
            'end_date',
            'departure_location',
            'role',
            'role_of_participant',
            'exclude_from_travel_plan',
            'parent_request',
            'multiple_conferences_rationale',
        ]
        widgets = {
            'user': forms.Select(attrs=chosen_js),
            'parent_request': forms.HiddenInput(),
            'start_date': forms.DateInput(attrs=attr_fp_date),
            'end_date': forms.DateInput(attrs=attr_fp_date),
            'role_of_participant': forms.Textarea(attrs=attr_row4),
            'phone': forms.TextInput(attrs={"class": "disappear-if-user input-phone"}),
            'first_name': forms.TextInput(attrs={"class": "disappear-if-user"}),
            'last_name': forms.TextInput(attrs={"class": "disappear-if-user"}),
            'email': forms.EmailInput(attrs={"class": "disappear-if-user"}),
            'exclude_from_travel_plan': forms.Select(choices=YES_NO_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        try:
            parent_request = kwargs.get("initial").get("parent_request")
        except AttributeError:
            parent_request = None

        if not parent_request:
            parent_request = kwargs.get("instance").parent_request

        user_choices = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        AuthUser.objects.all().order_by("last_name", "first_name")]
        user_choices.insert(0, tuple((None, "---")))
        super().__init__(*args, **kwargs)
        self.fields['user'].choices = user_choices

        # general trip infomation
        field_list = [
            'start_date',
            'end_date',
            'departure_location',
            'exclude_from_travel_plan',

        ]
        for field in field_list:
            self.fields[field].group = 1

        # traveller info
        field_list = [
            'user',
            'first_name',
            'last_name',
            'address',
            'phone',
            'email',
            'is_public_servant',
            'is_research_scientist',
            'company_name',
            'region',
        ]
        for field in field_list:
            self.fields[field].group = 2

        # justification
        field_list = [
            'role',
            'role_of_participant',
            'multiple_conferences_rationale',
        ]
        for field in field_list:
            self.fields[field].group = 3

        # are there any forgotten fields?
        for field in self.fields:
            try:
                self.fields[field].group
            except AttributeError:
                print(f'Adding label: "Unspecified" to field "{field}".')
                self.fields[field].group = 0


class TripForm(forms.ModelForm):
    class Meta:
        model = models.Conference
        exclude = ["fiscal_year", "is_verified", "verified_by", "cost_warning_sent"]
        widgets = {
            'start_date': forms.DateInput(attrs=attr_fp_date),
            'end_date': forms.DateInput(attrs=attr_fp_date),
            'registration_deadline': forms.DateInput(attrs=attr_fp_date),
            'abstract_deadline': forms.DateInput(attrs=attr_fp_date),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        abstract_deadline = cleaned_data.get("abstract_deadline")
        registration_deadline = cleaned_data.get("registration_deadline")

        if end_date < start_date:
            raise forms.ValidationError(_('The start date of the trip must occur after the end date.'))

        if abstract_deadline >= start_date:
            raise forms.ValidationError(_('The abstract deadline of the trip (if present) must occur before the start date.'))

        if registration_deadline >= start_date:
            raise forms.ValidationError(_('The registration deadline of the trip (if present) must occur before the start date.'))

        if abs((start_date - end_date).days) > 100:
            raise forms.ValidationError(_('The length of this trip is unrealistic.'))


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "------"),
        (1, "CFTS export (xlsx)"),
        # (2, "Print Travel Plan PDF"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    # report #1
    fiscal_year = forms.ChoiceField(required=False, label=_('Fiscal year'))
    # report #2
    user = forms.ChoiceField(required=False, label=_('DFO traveller (leave blank for all)'))

    def __init__(self, *args, **kwargs):
        fy_choices = [(fy.id, str(fy)) for fy in shared_models.FiscalYear.objects.all().order_by("id") if fy.trip_requests.count() > 0]
        # TRAVELLER_CHOICES = [(e['email'], "{}, {}".format(e['last_name'], e['first_name'])) for e in
        #                      models.Trip.objects.values("email", "first_name", "last_name").order_by("last_name", "first_name").distinct()]
        user_choices = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        AuthUser.objects.all().order_by("last_name", "first_name") if u.user_trip_requests.count() > 0]
        user_choices.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['fiscal_year'].choices = fy_choices
        self.fields['user'].choices = user_choices


class StatusForm(forms.ModelForm):
    class Meta:
        model = models.Status
        fields = "__all__"


StatusFormSet = modelformset_factory(
    model=models.Status,
    form=StatusForm,
    extra=1,
)


class ReviewerForm(forms.ModelForm):
    class Meta:
        model = models.Reviewer
        fields = [
            'trip_request',
            'order',
            'user',
            'role',
        ]
        widgets = {
            'trip_request': forms.HiddenInput(),
            'user': forms.Select(attrs=chosen_js),
        }


ReviewerFormSet = modelformset_factory(
    model=models.Reviewer,
    form=ReviewerForm,
    extra=1,
)


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        exclude = ["date_created", ]
        widgets = {
            'trip_request': forms.HiddenInput(),
        }


class HelpTextForm(forms.ModelForm):
    class Meta:
        model = models.HelpText
        fields = "__all__"
        widgets = {
            'eng_text': forms.Textarea(attrs={"rows": 4}),
            'fra_text': forms.Textarea(attrs={"rows": 4}),
        }


HelpTextFormSet = modelformset_factory(
    model=models.HelpText,
    form=HelpTextForm,
    extra=1,
)


class CostForm(forms.ModelForm):
    class Meta:
        model = models.Cost
        fields = "__all__"


CostFormSet = modelformset_factory(
    model=models.Cost,
    form=CostForm,
    extra=1,
)


class CostCategoryForm(forms.ModelForm):
    class Meta:
        model = models.CostCategory
        fields = "__all__"


CostCategoryFormSet = modelformset_factory(
    model=models.CostCategory,
    form=CostCategoryForm,
    extra=1,
)


class NJCRatesForm(forms.ModelForm):
    class Meta:
        model = models.NJCRates
        exclude = ['last_modified', ]


NJCRatesFormSet = modelformset_factory(
    model=models.NJCRates,
    form=NJCRatesForm,
    extra=0,
)


class TripRequestCostForm(forms.ModelForm):
    class Meta:
        model = models.TripRequestCost
        fields = "__all__"
        widgets = {
            'trip_request': forms.HiddenInput(),
            'rate_cad': forms.NumberInput(attrs={"class": "by-rate"}),
            'number_of_days': forms.NumberInput(attrs={"class": "by-rate"}),
            'amount_cad': forms.NumberInput(attrs={"class": "by-amount"}),
            # 'cost': forms.Select(attrs=chosen_js),
        }
