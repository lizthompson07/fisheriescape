
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
            'date_last_modified',
            'date_created',
        ]
        widgets = {
        }


class InteractionForm(forms.ModelForm):
    class Meta:
        model = models.Interaction
        exclude = [
            'date_last_modified',
            'date_created',
        ]
        widgets = {
            'date_of_meeting': forms.DateInput(attrs=attr_fp_date)
        }


class OrganizationForm(forms.ModelForm):
    asc_province = forms.MultipleChoiceField(required=False, label=_("Associated Province(s)"))
    category = forms.MultipleChoiceField(required=False, label=_("Categories"))
    area = forms.MultipleChoiceField(required=False, label=_("Area(s)"))

    class Meta:
        model = ml_models.Organization
        exclude = ["date_last_modified", "old_id", 'last_modified_by']
        widgets = {
            # multiselects
            'grouping': forms.SelectMultiple(attrs=multi_select_js),
            'regions': forms.SelectMultiple(attrs=multi_select_js),
            'sectors': forms.SelectMultiple(attrs=multi_select_js),
            'reserves': forms.SelectMultiple(attrs=multi_select_js),
            # dates
            'next_election': forms.TextInput(attrs=attr_fp_date),
            'new_coucil_effective_date': forms.TextInput(attrs=attr_fp_date)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['name_eng', 'category', 'name_ind', 'abbrev', 'address', 'mailing_address', 'city',
                           'postal_code', 'province', 'phone', 'fax', 'dfo_contact_instructions', 'notes',
                           'key_species', 'grouping', 'area', 'regions', 'asc_province'])

        self.fields['area'].widget = forms.SelectMultiple(attrs=multi_select_js)
        self.fields['category'].widget = forms.SelectMultiple(attrs=multi_select_js)
        self.fields['orgs'].widget = forms.SelectMultiple(attrs=multi_select_js)
        self.fields['asc_province'].widget = forms.SelectMultiple(attrs=multi_select_js)

        from ihub.views import get_ind_organizations
        org_choices_all = [(obj.id, obj) for obj in get_ind_organizations()]
        self.fields["orgs"].choices = org_choices_all

        area_choices = [(a.id, a) for a in models.Area.objects.all()]
        self.fields['area'].choices = area_choices

        category_choices = [(c.id, c) for c in models.OrgCategory.objects.all()]
        self.fields['category'].choices = category_choices

        province_choices = [(p.id, p) for p in shared_models.Province.objects.all()]
        self.fields['asc_province'].choices = province_choices


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


class PersonForm(forms.ModelForm):
    role = forms.CharField(required=True, label=_("Role"))

    class Meta:
        model = ml_models.Person
        exclude = ["date_last_modified", "old_id", 'last_modified_by']
        widgets = {
            'notes': forms.Textarea(attrs={"rows": "3"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['designation', 'role', 'first_name', 'last_name', 'phone_1', 'phone_2', 'email_1', 'email_2',
                           'cell', 'fax', 'language', 'notes'])


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
