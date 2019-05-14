from django import forms
from django.db.models import Q
from . import models
from shared_models import models as shared_models


class NewPublicationsForm(forms.ModelForm):
    pub_year = forms.DateField(widget=forms.DateInput(format='%Y'), input_formats=['%Y'])
    region = forms.ChoiceField()
    division = forms.ChoiceField()
    field_order = ['pub_year', 'pub_title', 'region', 'division']

    class Meta:
        model = models.Publications
        fields = [
            'pub_year',
            'pub_title',
            'last_modified_by',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'pub_title': forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        region_choices = [(r.id, str(r)) for r in shared_models.Region.objects.filter(Q(id=1) | Q(id=2))]
        region_choices.insert(0, tuple((None, "---")))

        division_choices = [(d.id, str(d)) for d in
                            shared_models.Division.objects.filter(Q(branch_id=1) | Q(branch_id=3)).order_by("branch__region", "name")]
        division_choices.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['region'].choices = region_choices
        self.fields['division'].choices = division_choices
