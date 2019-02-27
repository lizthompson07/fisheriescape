from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext as _

from . import models

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = [
            'name_eng',
            'name_fre',
            'name_ind',
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
            'key_species',
            'dfo_contact_instructions',
            'notes',
            'grouping',
            'regions',
            'sectors',
            'last_modified_by',
        ]
        widgets = {
            'key_species': forms.Textarea(attrs={"rows": 2}),
            'dfo_contact_instructions': forms.Textarea(attrs={"rows": 2}),
            'notes': forms.Textarea(attrs={"rows": 2}),
            'last_modified_by': forms.HiddenInput(),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = models.Person
        exclude = ["date_last_modified", ]

        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": 3}),
        }


class MemberForm(forms.ModelForm):
    class Meta:
        model = models.OrganizationMember
        exclude = [
            'roles',
            # 'notes',
            'date_last_modified',
        ]
        widgets = {
            'organization': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": 2}),
            'last_modified_by': forms.HiddenInput(),
        }


class OrganizationFormShort(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = [
            'name_eng',
            'name_fre',
            'name_ind',
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
        }


OrganizationFormSet = modelformset_factory(
    model=models.Organization,
    form=OrganizationFormShort,
    extra=1,
)


class RegionForm(forms.ModelForm):
    class Meta:
        model = models.Region
        fields = "__all__"


RegionFormSet = modelformset_factory(
    model=models.Region,
    form=RegionForm,
    extra=1,
)


class GroupingForm(forms.ModelForm):
    class Meta:
        model = models.Grouping
        fields = "__all__"


GroupingFormSet = modelformset_factory(
    model=models.Grouping,
    form=GroupingForm,
    extra=1,
)


class ReportSearchForm(forms.Form):
    PROVINCE_CHOICES = [(obj.id, str(obj)) for obj in models.Province.objects.all()]
    GROUPING_CHOICES = [(obj.id, str(obj)) for obj in models.Grouping.objects.all()]
    SECTOR_CHOICES = [(obj.id, str(obj)) for obj in models.Sector.objects.all()]
    REGION_CHOICES = [(obj.id, str(obj)) for obj in models.Region.objects.all()]

    REPORT_CHOICES = (
        (None, "------"),
        (1, "Master list custom export (xlsx)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)

    # report #1
    provinces = forms.MultipleChoiceField(required=False, choices=PROVINCE_CHOICES, label=_('Provinces - Leave blank for all'))
    groupings = forms.MultipleChoiceField(required=False, choices=GROUPING_CHOICES, label=_('Organization Grouping - Leave blank for all'))
    sectors = forms.MultipleChoiceField(required=False, choices=SECTOR_CHOICES, label=_('DFO Sectors - Leave blank for all'))
    regions = forms.MultipleChoiceField(required=False, choices=REGION_CHOICES, label=_('DFO Regions - Leave blank for all'))
    is_indigenous = forms.BooleanField(required=False, label=_('Indigenous Only'))
    species = forms.CharField(required=False, label=_('Key Species'))

# key_species
