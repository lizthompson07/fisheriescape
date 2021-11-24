from django import forms
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.utils.translation import gettext as _, gettext_lazy

from lib.functions.custom_functions import listrify
from masterlist import models as ml_models
from shared_models import models as shared_models
from . import models

chosen_js = {"class": "chosen-select-contains"}
multi_select_js = {"class": "multi-select"}
attr_fp_date = {"class": "fp-date", "placeholder": gettext_lazy("Click to select a date..")}


class EntryCreateForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        exclude = [
            'date_last_modified',
            'date_created',
        ]
        widgets = {
            'initial_date': forms.DateInput(attrs=attr_fp_date),
            'anticipated_end_date': forms.DateInput(attrs=attr_fp_date),
            'last_modified_by': forms.HiddenInput(),
            'created_by': forms.HiddenInput(),
            'organizations': forms.SelectMultiple(attrs=chosen_js),
            'regions': forms.SelectMultiple(attrs={'class': "multi-select"}),
            'sectors': forms.SelectMultiple(attrs=chosen_js),
        }

    def clean_organizations(self):
        organizations = self.cleaned_data['organizations']
        if not organizations:
            raise forms.ValidationError("You must select an organization!")
        return organizations

    def clean_sectors(self):
        sector = self.cleaned_data['sectors']
        if not sector:
            raise forms.ValidationError("You must select a sector!")
        return sector

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ihub.views import get_ind_organizations
        org_choices_all = [(obj.id, f'[{listrify(obj.regions.all())}] {obj.full_display_name}') for obj in get_ind_organizations()]
        self.fields["organizations"].choices = org_choices_all
        sector_choices = [(obj.id, f"{obj.region} - {obj.tname}") for obj in ml_models.Sector.objects.all()]
        self.fields["sectors"].choices = sector_choices

    def clean_organizations(self):
        organizations = self.cleaned_data['organizations']
        if not organizations:
            raise forms.ValidationError("You must select at least one organization!")
        return organizations

    def clean_sectors(self):
        sectors = self.cleaned_data['sectors']
        if not sectors:
            raise forms.ValidationError("You must select at least one sector!")
        return sectors


class EntryForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        exclude = [
            'date_last_modified',
            'date_created',
            'created_by',
        ]
        widgets = {
            'initial_date': forms.DateInput(attrs=attr_fp_date),
            'response_requested_by': forms.DateInput(attrs=attr_fp_date),
            'anticipated_end_date': forms.DateInput(attrs=attr_fp_date),
            'last_modified_by': forms.HiddenInput(),
            'organizations': forms.SelectMultiple(attrs=chosen_js),
            'regions': forms.SelectMultiple(attrs={'class': "multi-select"}),
            'sectors': forms.SelectMultiple(attrs=chosen_js),
        }

    def clean_organizations(self):
        organizations = self.cleaned_data['organizations']
        if not organizations:
            raise forms.ValidationError("You must select an organization!")
        return organizations

    def clean_sectors(self):
        sector = self.cleaned_data['sectors']
        if not sector:
            raise forms.ValidationError("You must select a sector!")
        return sector

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ihub.views import get_ind_organizations
        org_choices_all = [(obj.id, f'[{listrify(obj.regions.all())}] {obj.full_display_name}') for obj in get_ind_organizations()]
        self.fields["organizations"].choices = org_choices_all
        sector_choices = [(obj.id, f"{obj.region} - {obj.tname}") for obj in ml_models.Sector.objects.all()]
        self.fields["sectors"].choices = sector_choices
        self.fields['initial_date'].widget.format = '%Y-%m-%d'
        self.fields['anticipated_end_date'].widget.format = '%Y-%m-%d'
        self.fields['response_requested_by'].widget.format = '%Y-%m-%d'

    def clean_organizations(self):
        organizations = self.cleaned_data['organizations']
        if not organizations:
            raise forms.ValidationError("You must select at least one organization!")
        return organizations

    def clean_sectors(self):
        sectors = self.cleaned_data['sectors']
        if not sectors:
            raise forms.ValidationError("You must select at least one sector!")
        return sectors

class NoteForm(forms.ModelForm):
    class Meta:
        model = models.EntryNote
        fields = "__all__"
        widgets = {
            'entry': forms.HiddenInput(),
            'author': forms.HiddenInput(),
        }


class ReportSearchForm(forms.Form):
    # ORG_CHOICES = [(None, "---"), ]
    field_order = ["report", "fiscal_year", "statuses", "organizations", "entry_types", "single_org"]

    def __init__(self, *args, **kwargs):
        from .views import get_ind_organizations

        super().__init__(*args, **kwargs)

        report_choices = (
            (None, "------"),
            (1, _("Capacity Report (Excel Spreadsheet)")),
            (2, _("Organizational Report / Cue Card (PDF)")),
            (3, _("iHub Summary Report")),
            (6, _("Engagement Update Log")),
            (7, _("Consultation Instructions (PDF)")),
            (8, _("Consultation Instructions - Mail Merge (xlsx)")),
            (9, _("Consultation Report (xlsx)")),
        )
        format_choices = (
            (None, "------"),
            ('pdf', "Adobe PDF (pdf)"),
            ('xlsx', "Excel (xlsx)"),
        )

        entry_region_choices = [(obj.id, str(obj)) for obj in shared_models.Region.objects.filter(entries__isnull=False).distinct()]
        org_region_choices = [(obj.id, str(obj)) for obj in shared_models.Region.objects.filter(organizations__isnull=False).distinct()]

        org_choices_all = [(obj.id, f'[{listrify(obj.regions.all())}] {obj.full_display_name}') for obj in get_ind_organizations()]
        org_choices_has_entry = [(obj.id, f'[{listrify(obj.regions.all())}] {obj.full_display_name}') for obj in get_ind_organizations() if
                                 obj.entries.count() > 0]
        org_choices_has_ci = [(obj.id, f'[{listrify(obj.regions.all())}] {obj.full_display_name}') for obj in get_ind_organizations() if
                              hasattr(obj, "consultation_instructions")]

        sector_choices = [(obj.id, f"{obj.region} - {obj.tname}") for obj in ml_models.Sector.objects.all() if obj.entries.count() > 0]
        status_choices = [(obj.id, obj) for obj in models.Status.objects.all() if obj.entries.count() > 0]
        entry_type_choices = [(obj.id, obj) for obj in models.EntryType.objects.all() if obj.entries.count() > 0]

        note_type_choices = list(models.EntryNote.TYPE_CHOICES)
        # we need to modify one of the descriptions...
        note_type_choices.remove((models.EntryNote.INTERNAL, _('Internal')))
        note_type_choices.append((models.EntryNote.INTERNAL, _('Internal (** for internal reports only)')))
        note_type_choices.remove((models.EntryNote.FOLLOWUP, _('Follow-up (*)')))

        note_status_choices = [(obj.id, obj) for obj in models.Status.objects.all() if obj.entry_notes.exists()]

        note_type_choices_all = list(models.EntryNote.TYPE_CHOICES)
        # we need to modify one of the descriptions...
        note_type_choices_all.remove((models.EntryNote.INTERNAL, _('Internal')))
        note_type_choices_all.append((models.EntryNote.INTERNAL, _('Internal (** for internal reports only)')))

        self.fields['report'] = forms.ChoiceField(required=True, choices=report_choices)
        self.fields['format'] = forms.ChoiceField(required=False, choices=format_choices)
        self.fields['from_date'] = forms.CharField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
        self.fields['to_date'] = forms.CharField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
        self.fields['org_regions'] = forms.MultipleChoiceField(required=False,
                                                               label='Only include entries whose organizations belong to the following region(s)',
                                                               choices=org_region_choices,
                                                               help_text="Leave blank for all.",
                                                               widget=forms.SelectMultiple(attrs=chosen_js)
                                                               )

        self.fields['entry_regions'] = forms.MultipleChoiceField(required=False,
                                                                 label='Only include entries belonging to the following region(s)',
                                                                 choices=entry_region_choices,
                                                                 help_text="Leave blank for all",
                                                                 widget=forms.SelectMultiple(attrs=chosen_js)
                                                                 )
        self.fields['sectors'] = forms.MultipleChoiceField(required=False,
                                                           label='List of sectors (w/ entries)',
                                                           choices=sector_choices,
                                                           help_text="Leave blank for all",
                                                           widget=forms.SelectMultiple(attrs=chosen_js)
                                                           )
        self.fields['organizations'] = forms.MultipleChoiceField(required=False,
                                                                 label='List of organizations (w/ entries)',
                                                                 choices=org_choices_has_entry,
                                                                 help_text="Leave blank for all",
                                                                 widget=forms.SelectMultiple(attrs=chosen_js)
                                                                 )
        self.fields['orgs_w_consultation_instructions'] = forms.MultipleChoiceField(required=False,
                                                                                    label='List of organizations (w/ consultation instructions)',
                                                                                    choices=org_choices_has_ci,
                                                                                    help_text="Leave blank for all",
                                                                                    widget=forms.SelectMultiple(attrs=chosen_js)
                                                                                    )
        self.fields['statuses'] = forms.MultipleChoiceField(required=False,
                                                            label='Status(es)',
                                                            choices=status_choices,
                                                            help_text="Leave blank for all",
                                                            widget=forms.SelectMultiple(attrs=chosen_js)

                                                            )
        self.fields['entry_types'] = forms.MultipleChoiceField(required=False,
                                                               label='Entry Type(s)',
                                                               choices=entry_type_choices,
                                                               help_text="Leave blank for all",
                                                               widget=forms.SelectMultiple(attrs=chosen_js)

                                                               )
        self.fields['single_org'] = forms.ChoiceField(
            required=False, label='Organization', choices=org_choices_all, widget=forms.Select(attrs=chosen_js)
        )

        self.fields['entry_note_types'] = forms.MultipleChoiceField(required=False,
                                                                    label='Include which types of entry notes',
                                                                    choices=note_type_choices,
                                                                    help_text="Leave blank for all",
                                                                    widget=forms.SelectMultiple(attrs=chosen_js)
                                                                    )
        self.fields['entry_note_types_all'] = forms.MultipleChoiceField(required=False,
                                                                        label='Include which types of entry notes',
                                                                        choices=note_type_choices_all,
                                                                        help_text="Leave blank for all",
                                                                        widget=forms.SelectMultiple(attrs=chosen_js)
                                                                        )
        self.fields['entry_note_statuses'] = forms.MultipleChoiceField(required=False,
                                                                       label='Include entry notes with which status(es)',
                                                                       choices=note_status_choices,
                                                                       help_text="Leave blank for all",
                                                                       widget=forms.SelectMultiple(attrs=chosen_js)
                                                                       )
        self.fields['report_title'] = forms.CharField(required=False)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = ml_models.Organization
        exclude = ["date_last_modified", "old_id", 'last_modified_by']
        widgets = {
            # multiselects
            'grouping': forms.SelectMultiple(attrs=multi_select_js),
            'regions': forms.SelectMultiple(attrs=multi_select_js),
            'sectors': forms.SelectMultiple(attrs=multi_select_js),
            'reserves': forms.SelectMultiple(attrs=multi_select_js),
            'orgs': forms.SelectMultiple(attrs=multi_select_js),
            # dates
            'next_election': forms.TextInput(attrs=attr_fp_date),
            'new_coucil_effective_date': forms.TextInput(attrs=attr_fp_date)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ihub.views import get_ind_organizations
        org_choices_all = [(obj.id, obj) for obj in get_ind_organizations()]
        self.fields["orgs"].choices = org_choices_all


class PersonForm(forms.ModelForm):
    class Meta:
        model = ml_models.Person
        fields = [
            "designation",
            "first_name",
            "last_name",
            "phone_1",
            "phone_2",
            "email_1",
            "email_2",
            "cell",
            "fax",
            "language",
            "notes",
        ]
        widgets = {
            'notes': forms.Textarea(attrs={"rows": "3"}),
        }


class EntryPersonForm(forms.ModelForm):
    # save_then_go_OT = forms.CharField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = models.EntryPerson
        fields = "__all__"
        labels = {
            "user": _("DFO employee"),
        }
        widgets = {
            'entry': forms.HiddenInput(),
            'user': forms.Select(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        User.objects.all().order_by("last_name", "first_name")]
        USER_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all().order_by("last_name", "first_name")
        self.fields['user'].choices = USER_CHOICES


class MemberForm(forms.ModelForm):
    # save_then_go_OT = forms.CharField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = ml_models.OrganizationMember
        exclude = ["date_last_modified", ]
        widgets = {
            'person': forms.Select(attrs=chosen_js),
            'organization': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": "3"}),
        }
        labels = {
            'person': gettext_lazy("Select a contact"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['person'].required = False


class InstructionForm(forms.ModelForm):
    class Meta:
        model = ml_models.ConsultationInstruction
        exclude = [
            'date_last_modified',
        ]
        widgets = {
            'organization': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": 3}),
            'last_modified_by': forms.HiddenInput(),
        }


class ConsultationRoleForm(forms.ModelForm):
    class Meta:
        model = ml_models.ConsultationRole
        exclude = ["date_last_modified"]
        widgets = {
            'member': forms.HiddenInput(),
            'organization': forms.Select(attrs=chosen_js),
            'last_modified_by': forms.HiddenInput(),
        }
        labels = {
            'organization': "For which organization?"
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"
        widgets = {
            'entry': forms.HiddenInput(),
            'date_uploaded': forms.HiddenInput(),
        }


class SectorForm(forms.ModelForm):
    class Meta:
        model = ml_models.Sector
        fields = "__all__"


SectorFormSet = modelformset_factory(
    model=ml_models.Sector,
    form=SectorForm,
    extra=1,
)


# class MemberRoleForm(forms.ModelForm):
#     class Meta:
#         model = models.MemberRole
#         fields = "__all__"
#
#
# MemberRoleFormSet = modelformset_factory(
#     model=models.MemberRole,
#     form=MemberRoleForm,
#     extra=1,
# )


class OrganizationFormShort(forms.ModelForm):
    class Meta:
        model = ml_models.Organization
        fields = [
            'name_eng',
            'name_ind',
            'former_name',
            'nation',
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
            'next_election',
            'election_term',
            'population_on_reserve',
            'population_off_reserve',
            'population_other_reserve',
            'fin',
            'notes',
            'grouping',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={"rows": 2}),
            'next_election': forms.TextInput(attrs=attr_fp_date),
        }


OrganizationFormSet = modelformset_factory(
    model=ml_models.Organization,
    form=OrganizationFormShort,
    extra=1,
)


class StatusForm(forms.ModelForm):
    class Meta:
        model = models.Status
        fields = "__all__"


StatusFormSet = modelformset_factory(
    model=models.Status,
    form=StatusForm,
    extra=1,
)


class EntryTypeForm(forms.ModelForm):
    class Meta:
        model = models.EntryType
        fields = "__all__"


EntryTypeFormSet = modelformset_factory(
    model=models.EntryType,
    form=EntryTypeForm,
    extra=1,
)


class FundingPurposeForm(forms.ModelForm):
    class Meta:
        model = models.FundingPurpose
        fields = "__all__"


FundingPurposeFormSet = modelformset_factory(
    model=models.FundingPurpose,
    form=FundingPurposeForm,
    extra=1,
)


class RegionForm(forms.ModelForm):
    class Meta:
        model = shared_models.Region
        fields = "__all__"


RegionFormSet = modelformset_factory(
    model=shared_models.Region,
    form=RegionForm,
    extra=1,
)


class ReserveForm(forms.ModelForm):
    class Meta:
        model = ml_models.Reserve
        fields = "__all__"


ReserveFormSet = modelformset_factory(
    model=ml_models.Reserve,
    form=ReserveForm,
    extra=1,
)


class GroupingForm(forms.ModelForm):
    class Meta:
        model = ml_models.Grouping
        fields = "__all__"


GroupingFormSet = modelformset_factory(
    model=ml_models.Grouping,
    form=GroupingForm,
    extra=1,
)


class NationForm(forms.ModelForm):
    class Meta:
        model = ml_models.Nation
        fields = "__all__"


NationFormSet = modelformset_factory(
    model=ml_models.Nation,
    form=NationForm,
    extra=1,
)


class FundingProgramForm(forms.ModelForm):
    class Meta:
        model = models.FundingProgram
        fields = "__all__"


FundingProgramFormSet = modelformset_factory(
    model=models.FundingProgram,
    form=FundingProgramForm,
    extra=1,
)


class RelationshipRatingForm(forms.ModelForm):
    class Meta:
        model = ml_models.RelationshipRating
        fields = "__all__"


RelationshipRatingFormSet = modelformset_factory(
    model=ml_models.RelationshipRating,
    form=RelationshipRatingForm,
    extra=1,
)
