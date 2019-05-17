from django import forms
from django.db.models import Q
from django.forms import widgets
from . import models
from shared_models import models as shared_models


class UpperCaseField(forms.CharField):
    def to_python(self, value):
        return value.upper()


class NewPublicationsForm(forms.ModelForm):
    pub_year = forms.DateField(widget=forms.DateInput(format='%Y'), input_formats=['%Y'])
    region = forms.ChoiceField()
    field_order = ['pub_year', 'pub_title', 'pub_abstract', 'region', 'division', 'date_last_modified']

    class Meta:
        model = models.Publications
        fields = ['pub_year', 'pub_title', 'pub_abstract', 'region', 'division']
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'pub_title': forms.Textarea(attrs={"rows": 2}),
            'pub_abstract': forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        region_choices = [(r.id, str(r)) for r in shared_models.Region.objects.filter(Q(id=1) | Q(id=2))]
        region_choices.insert(0, tuple((None, "---")))

        division_choices = [(d.id, str(d)) for d in
                            shared_models.Division.objects.filter(Q(branch_id=1) | Q(branch_id=3)).order_by("branch__region", "name")]
        division_choices.insert(0, tuple((None, "---")))

        self.fields['region'].choices = region_choices
        self.fields['division'].choices = division_choices


class PublicationsSubmitForm(forms.ModelForm):
    class Meta:
        model = models.Publications
        fields = [
            'last_modified_by',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class PublicationsForm(forms.ModelForm):

    class Meta:
        model = models.Publications
        fields = [
            'pub_year',
            'pub_title',
            'last_modified_by',
        ]
        excludes = [
            'date_last_modified',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'pub_title': forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LookupForm(forms.ModelForm):
    class Meta:
        model = models.Theme
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._meta.model = kwargs['initial']['lookup']

        values = [(t.id, t.name) for t in self._meta.model.objects.all()]

        self.fields['name'] = forms.MultipleChoiceField(required=True, choices=values,
                                                        widget=widgets.SelectMultiple(attrs={'size': 15}))


class LookupNew(forms.ModelForm):

    name = UpperCaseField(required=True)

    class Meta:
        model = models.Theme
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._meta.model = kwargs['initial']['lookup']
