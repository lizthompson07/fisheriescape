from django import forms
from django.forms import modelformset_factory

from . import models
from django.contrib.auth.models import User

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
            'key_species':forms.Textarea(attrs={"rows":2}),
            'dfo_contact_instructions':forms.Textarea(attrs={"rows":2}),
            'notes':forms.Textarea(attrs={"rows":2}),
            'last_modified_by':forms.HiddenInput(),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = models.Person
        fields = "__all__"


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


class MemberRoleForm(forms.ModelForm):
    class Meta:
        model = models.MemberRole
        fields = "__all__"


MemberRoleFormSet = modelformset_factory(
    model=models.MemberRole,
    form=MemberRoleForm,
    extra=1,
)


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
