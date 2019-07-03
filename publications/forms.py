from django import forms
from django.db.models import Q
from django.forms import widgets
from . import models
from shared_models import models as shared_models


class UpperCaseField(forms.CharField):
    def to_python(self, value):
        return value.upper()


class NewProjectForm(forms.ModelForm):
    region = forms.ChoiceField()
    field_order = ['title', 'abstract', 'method', 'year', 'region', 'division', 'date_last_modified']

    class Meta:
        model = models.Project
        fields = ['title', 'abstract', 'method', 'year', 'region', 'division']
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'title': forms.Textarea(attrs={"rows": 1}),
            'abstract': forms.Textarea(attrs={"rows": 4}),
            'method': forms.Textarea(attrs={"rows": 4}),
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

        print(kwargs)
        if 'key' in kwargs['initial'].keys() and kwargs['initial']['key']:
            obj = models.Project.objects.get(pk=kwargs['initial']['key'])
            print(obj.division.all())


class ProjectSubmitForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = [
            'last_modified_by',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
        }


class ProjectForm(forms.ModelForm):

    class Meta:
        model = models.Project
        fields = [
            'title',
            'last_modified_by',
        ]
        excludes = [
            'date_last_modified',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'title': forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LookupForm(forms.ModelForm):
    name = UpperCaseField(required=False, label="Add a new item")
    mult_name = forms.MultipleChoiceField(required=False, label="Select one or more existing items "
                                          "(holding down ctrl-key)", widget=widgets.SelectMultiple(attrs={'size': 13}))

    class Meta:
        model = models.Theme
        fields = ['mult_name','name']

    def __init__(self, *args, **kwargs):
        self._meta.model = kwargs['initial']['lookup']
        super().__init__(*args, **kwargs)

        values = [(t.id, t.name) for t in self._meta.model.objects.all()]
        self.fields['mult_name'].choices = values


class TextForm(forms.ModelForm):
    value = forms.Textarea()

    class Meta:
        model = models.Site
        fields = ['value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._meta.model = kwargs['initial']['lookup']
