import inspect

from django import forms
from maret import models
from masterlist import models as ml_models
from shared_models import models as shared_models
from django.forms import modelformset_factory
from django.utils.translation import gettext as _, gettext_lazy

chosen_js = {"class": "chosen-select-contains"}
multi_select_js = {"class": "multi-select"}
attr_fp_date = {"class": "fp-date", "placeholder": gettext_lazy("Click to select a date..")}


class CommitteeForm(forms.ModelForm):
    class Meta:
        model = models.Committee
        exclude = [
            'last_modified'
        ]
        widgets = {
            'external_chair': forms.SelectMultiple(attrs=chosen_js),
            'dfo_liaison': forms.SelectMultiple(attrs=chosen_js),
            'last_modified_by': forms.HiddenInput(),
            'external_organization': forms.SelectMultiple(attrs=chosen_js),
            'external_contact': forms.SelectMultiple(attrs=chosen_js),
            'other_dfo_participants': forms.SelectMultiple(attrs=chosen_js)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['name', 'main_topic', 'species', 'lead_region', 'branch', 'division', 'area_office',
                           'area_office_program', 'other_dfo_branch', 'other_dfo_areas', 'other_dfo_regions',
                           'dfo_national_sectors', 'dfo_role', 'is_dfo_chair', 'external_chair', 'external_contact',
                           'external_organization', 'dfo_liaison', 'other_dfo_participants',
                           'first_nation_participation', 'municipal_participation', 'provincial_participation',
                           'other_federal_participation', 'meeting_frequency', 'are_tor', 'location_of_tor',
                           'main_actions', 'comments',
                           ])

        self.fields['main_topic'].widget.attrs['size'] = '6'
        self.fields['species'].widget.attrs['size'] = '6'
        self.fields['other_dfo_branch'].widget.attrs['size'] = '6'
        self.fields['other_dfo_regions'].widget.attrs['size'] = '6'
        self.fields['other_dfo_areas'].widget.attrs['size'] = '6'

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["dfo_liaison"] is None:
            self.add_error('dfo_liaison', _("DFO liaison/secretariat is required"))

        # sync these fields:
        if cleaned_data["external_chair"].exists():
            cleaned_data["external_contact"] = (cleaned_data["external_contact"] |
                                                cleaned_data["external_chair"]).distinct()

        return cleaned_data


class InteractionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # changes number of rows / height of multiple select widget:
        self.fields['main_topic'].widget.attrs['size'] = '8'
        self.fields['species'].widget.attrs['size'] = '8'
        self.fields['other_dfo_branch'].widget.attrs['size'] = '6'
        self.fields['other_dfo_regions'].widget.attrs['size'] = '6'
        self.fields['other_dfo_areas'].widget.attrs['size'] = '6'
        self.order_fields(['description', 'interaction_type', 'committee', 'date_of_meeting', 'main_topic', 'species', 'lead_region',
                           'branch', 'division', 'area_office', 'area_office_program', 'other_dfo_branch',
                           'other_dfo_areas', 'other_dfo_regions', 'dfo_national_sectors', 'dfo_role',
                           'external_contact', 'external_organization', 'dfo_liaison', 'other_dfo_participants',
                           'action_items', 'comments'
                           ])

    class Meta:
        model = models.Interaction
        exclude = [
            'date_last_modified',
            'date_created',
        ]
        widgets = {
            'date_of_meeting': forms.DateInput(attrs=attr_fp_date),
            'last_modified': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
            'committee': forms.Select(attrs=chosen_js),
            'dfo_role': forms.Select(attrs=chosen_js),
            'dfo_liaison': forms.SelectMultiple(attrs=chosen_js),
            'other_dfo_participants': forms.SelectMultiple(attrs=chosen_js),
            'external_organization': forms.SelectMultiple(attrs=chosen_js),
            'external_contact': forms.SelectMultiple(attrs=chosen_js),
        }


class OrganizationForm(forms.ModelForm):
    asc_province = forms.MultipleChoiceField(required=False, label=_("Associated Province(s)"))
    category = forms.MultipleChoiceField(required=False, label=_("Categories"))
    area = forms.MultipleChoiceField(required=False, label=_("Area(s)"))
    email = forms.EmailField(required=False, label=_("E-mail"))
    committee = forms.MultipleChoiceField(required=False, label=_("Committees/Working Groups"))

    class Meta:
        model = ml_models.Organization
        exclude = ["date_last_modified", "old_id", 'relationship_rating', 'reserves']
        widgets = {
            # multiselects
            'grouping': forms.SelectMultiple(attrs=multi_select_js),
            'regions': forms.SelectMultiple(attrs=multi_select_js),
            'sectors': forms.SelectMultiple(attrs=multi_select_js),
            'reserves': forms.SelectMultiple(attrs=multi_select_js),
            # dates
            'dfo_contact_instructions': forms.HiddenInput(),
            'next_election': forms.TextInput(attrs=attr_fp_date),
            'new_coucil_effective_date': forms.TextInput(attrs=attr_fp_date),
            'last_modified': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['name_eng', 'category', 'grouping', 'name_ind', 'abbrev', 'email', 'address', 'mailing_address', 'city',
                           'postal_code', 'province', 'phone', 'fax', 'notes',
                           'key_species', 'area', 'regions', 'asc_province', 'committee'])

        self.fields['area'].widget = forms.SelectMultiple(attrs=multi_select_js)
        self.fields['category'].widget = forms.SelectMultiple(attrs=multi_select_js)
        self.fields['orgs'].widget = forms.SelectMultiple(attrs=multi_select_js)
        self.fields['asc_province'].widget = forms.SelectMultiple(attrs=multi_select_js)
        self.fields['committee'].widget = forms.SelectMultiple(attrs=chosen_js)

        org_choices_all = [(obj.id, obj) for obj in ml_models.Organization.objects.all()]
        self.fields["orgs"].choices = org_choices_all

        area_choices = [(a.id, a) for a in models.Area.objects.all()]
        self.fields['area'].choices = area_choices

        category_choices = [(c.id, c) for c in models.OrgCategory.objects.all()]
        self.fields['category'].choices = category_choices

        province_choices = [(p.id, p) for p in shared_models.Province.objects.all()]
        self.fields['asc_province'].choices = province_choices

        self.fields['committee'].choices = [(c.id, c) for c in models.Committee.objects.all()]



class MemberForm(forms.ModelForm):
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

    def clean(self):
        cleaned_data = super(MemberForm, self).clean()
        if not cleaned_data["person"]:
            self.add_error("person", _("Person is required."))
        return cleaned_data


class PersonForm(forms.ModelForm):
    committee = forms.MultipleChoiceField(required=False, label=_("Committees/Working Groups"))

    class Meta:
        model = ml_models.Person
        exclude = ["date_last_modified", "old_id",  'connected_user']
        widgets = {
            'organizations': forms.SelectMultiple(attrs=chosen_js),
            'notes': forms.Textarea(attrs={"rows": "3"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['designation', 'first_name', 'last_name', 'phone_1', 'phone_2', 'cell', 'email_1',
                           'email_2', 'fax', 'language', 'notes', 'committee'])
        self.fields['organizations'].label = _("Organization Membership")
        self.fields['committee'].widget = forms.SelectMultiple(attrs=chosen_js)
        self.fields['committee'].choices = [(c.id, c) for c in models.Committee.objects.all()]


class TopicForm(forms.ModelForm):
    class Meta:
        model = models.DiscussionTopic
        fields = "__all__"


TopicFormSet = modelformset_factory(
    model=models.DiscussionTopic,
    form=TopicForm,
    extra=3,
)


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"


SpeciesFormSet = modelformset_factory(
    model=models.Species,
    form=SpeciesForm,
    extra=3,
)


class OrgCategoryForm(forms.ModelForm):
    class Meta:
        model = models.OrgCategory
        fields = "__all__"


OrgCategoriesFormSet = modelformset_factory(
    model=models.OrgCategory,
    form=OrgCategoryForm,
    extra=3,
)


class AreaForm(forms.ModelForm):
    class Meta:
        model = models.AreaOffice
        fields = "__all__"


AreasFormSet = modelformset_factory(
    model=models.AreaOffice,
    form=AreaForm,
    extra=3,
)


class AreaOfficeForm(forms.ModelForm):
    class Meta:
        model = models.AreaOffice
        fields = "__all__"


AreaOfficesFormSet = modelformset_factory(
    model=models.AreaOffice,
    form=AreaOfficeForm,
    extra=3,
)


class AreaOfficeProgramForm(forms.ModelForm):
    class Meta:
        model = models.AreaOfficeProgram
        fields = "__all__"


AreaOfficesProgramFormSet = modelformset_factory(
    model=models.AreaOfficeProgram,
    form=AreaOfficeProgramForm,
    extra=3,
)


class HelpTextPopForm(forms.ModelForm):

    class Meta:
        model = models.HelpText
        fields = "__all__"
        widgets = {
            'model': forms.HiddenInput(),
            'field_name': forms.HiddenInput(),
            'eng_text': forms.Textarea(attrs={"rows": 2}),
            'fra_text': forms.Textarea(attrs={"rows": 2}),
        }


class HelpTextForm(forms.ModelForm):

    model = None

    class Meta:
        fields = "__all__"
        widgets = {
            'eng_text': forms.Textarea(attrs={"rows": 2}),
            'fra_text': forms.Textarea(attrs={"rows": 2}),
        }


HelpTextFormset = modelformset_factory(
    model=models.HelpText,
    form=HelpTextForm,
    extra=1,
)


class MaretUserForm(forms.ModelForm):
    class Meta:
        model = models.MaretUser
        fields = "__all__"
        widgets = {
            'user': forms.Select(attrs=chosen_js),
        }


MaretUserFormset = modelformset_factory(
    model=models.MaretUser,
    form=MaretUserForm,
    extra=1,
)