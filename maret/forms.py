
from django import forms
from maret import models
from masterlist import models as ml_models
from django.forms import modelformset_factory
from django.utils.translation import gettext as _, gettext_lazy

chosen_js = {"class": "chosen-select-contains"}
multi_select_js = {"class": "multi-select"}
attr_fp_date = {"class": "fp-date", "placeholder": gettext_lazy("Click to select a date..")}


class CommitteeCreateForm(forms.ModelForm):
    class Meta:
        model = models.Committee
        exclude = [
            'date_last_modified',
            'date_created',
        ]
        widgets = {
        }


class InteractionCreateForm(forms.ModelForm):
    class Meta:
        model = models.Interaction
        exclude = [
            'date_last_modified',
            'date_created',
        ]
        widgets = {
        }


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
