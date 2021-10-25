
from django import forms
from maret import models
from masterlist import models as ml_models
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
            'orgs': forms.SelectMultiple(attrs=multi_select_js),
            'area': forms.SelectMultiple(attrs=multi_select_js),
            # dates
            'next_election': forms.TextInput(attrs=attr_fp_date),
            'new_coucil_effective_date': forms.TextInput(attrs=attr_fp_date)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['name_eng', 'name_ind', 'abbrev', 'address', 'mailing_address', 'city', 'postal_code',
                           'province', 'phone', 'fax', 'dfo_contact_instructions', 'notes', 'key_species', 'grouping',
                           'area'])
        from ihub.views import get_ind_organizations
        org_choices_all = [(obj.id, obj) for obj in get_ind_organizations()]
        self.fields["orgs"].choices = org_choices_all

        area_choices = [(y.pk, y.tname,) for idx, y in enumerate(models.Area.objects.all())]
        self.fields['area'].choices = area_choices


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


class TopicForm(forms.ModelForm):
    class Meta:
        model = models.DiscussionTopic
        fields = "__all__"


TopicFormSet = modelformset_factory(
    model=models.DiscussionTopic,
    form=TopicForm,
    extra=1,
)


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = models.Species
        fields = "__all__"


SpeciesFormSet = modelformset_factory(
    model=models.Species,
    form=SpeciesForm,
    extra=1,
)


class AreaForm(forms.ModelForm):
    class Meta:
        model = models.Area
        fields = "__all__"


AreaFormSet = modelformset_factory(
    model=models.Area,
    form=AreaForm,
    extra=1,
)
