from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext as _
from shared_models import models as shared_models
from masterlist import models as ml_models
from . import models

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = ml_models.Organization
        fields = [
            'name_eng',
            'name_fre',
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
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


class MemberForm(forms.ModelForm):
    class Meta:
        model = ml_models.OrganizationMember
        fields = [
            'person',
            'organization',
            'role',
            # 'role_notes',
            'notes',
            'last_modified_by',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={"rows": 2}),
            'organization': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = ml_models.Person
        fields = [
            "designation",
            "first_name",
            "last_name",
            "email_1",
            "email_2",
            "phone_1",
            "phone_2",
            "cell",
            "fax",
            "language",
            "notes",
            "old_id",
        ]

        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": 3}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = [
            'path_number',
            'program_reference_number',
            'organization',
            'title',
            'program',
            'language',
            'status',
            'regions',
            'start_year',
            'project_length',
            'date_completed',
            'last_modified_by',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class NewProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = [
            'regions',
            'path_number',
            'program_reference_number',
            'organization',
            'title',
            'program',
            'language',
            'status',
            'start_year',
            'requested_funding_y1',
            'requested_funding_y2',
            'requested_funding_y3',
            'last_modified_by',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }

class ProjectPersonForm(forms.ModelForm):
    class Meta:
        model = models.ProjectPerson
        fields = [
            'person',
            'project',
            'role',
            'last_modified_by',
        ]
        widgets = {
            'project': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
        }