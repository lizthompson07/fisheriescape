from django import forms
from django.contrib.auth.models import User
from django.core import validators
from . import models
from shared_models import models as shared_models


class ResourceCreateForm(forms.ModelForm):
    add_custodian = forms.BooleanField(required=False, label="Add yourself as custodian")
    add_point_of_contact = forms.BooleanField(required=False, label="Add Regional Data Manager as a Point of Contact")

    class Meta:
        model = models.Resource
        exclude = [
            'file_identifier',
            'uuid',
            'date_verified',
            # 'date_last_modified',
            'fgp_publication_date',
            'citations',
            'keywords',
            'people',
            'flagged_4_publication',
            'flagged_4_deletion',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'title_eng': forms.Textarea(attrs={"rows": 5}),
            'title_fre': forms.Textarea(attrs={"rows": 5}),
            "purpose_eng": forms.Textarea(attrs={"rows": 5}),
            "purpose_fre": forms.Textarea(attrs={"rows": 5}),
            "descr_eng": forms.Textarea(attrs={"rows": 8}),
            "descr_fre": forms.Textarea(attrs={"rows": 8}),
            "physical_sample_descr_eng": forms.Textarea(attrs={"rows": 5}),
            "physical_sample_descr_fre": forms.Textarea(attrs={"rows": 5}),
            "sampling_method_eng": forms.Textarea(attrs={"rows": 5}),
            "sampling_method_fre": forms.Textarea(attrs={"rows": 5}),
            "resource_constraint_eng": forms.Textarea(attrs={"rows": 5}),
            "resource_constraint_fre": forms.Textarea(attrs={"rows": 5}),
            "qc_process_descr_eng": forms.Textarea(attrs={"rows": 5}),
            "qc_process_descr_fre": forms.Textarea(attrs={"rows": 5}),
            "storage_envr_notes": forms.Textarea(attrs={"rows": 5}),
            "parameters_collected_eng": forms.Textarea(attrs={"rows": 5}),
            "parameters_collected_fre": forms.Textarea(attrs={"rows": 5}),
            "additional_credit": forms.Textarea(attrs={"rows": 5}),
            "analytic_software": forms.Textarea(attrs={"rows": 5}),
            "notes": forms.Textarea(attrs={"rows": 5}),
        }
        labels = {
            "section": "Section (Region / Branch / Division / Section)"
        }

    def __init__(self, *args, **kwargs):
        SECTION_CHOICES = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch", "division", "name")]
        SECTION_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = SECTION_CHOICES


class ResourceForm(forms.ModelForm):
    class Meta:
        model = models.Resource
        exclude = [
            'file_identifier',
            'uuid',
            'date_verified',
            # 'date_last_modified',
            'fgp_publication_date',
            'citations',
            'keywords',
            'people',
            'flagged_4_publication',
            'flagged_4_deletion',
            'completedness_rating',
            'completedness_report',
            'translation_needed',
        ]
        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'date_last_modified': forms.HiddenInput(),
            'title_eng': forms.Textarea(attrs={"rows": 5}),
            'title_fre': forms.Textarea(attrs={"rows": 5}),
            "purpose_eng": forms.Textarea(attrs={"rows": 5}),
            "purpose_fre": forms.Textarea(attrs={"rows": 5}),
            "descr_eng": forms.Textarea(attrs={"rows": 8}),
            "descr_fre": forms.Textarea(attrs={"rows": 8}),
            "physical_sample_descr_eng": forms.Textarea(attrs={"rows": 5}),
            "physical_sample_descr_fre": forms.Textarea(attrs={"rows": 5}),
            "sampling_method_eng": forms.Textarea(attrs={"rows": 5}),
            "sampling_method_fre": forms.Textarea(attrs={"rows": 5}),
            "resource_constraint_eng": forms.Textarea(attrs={"rows": 5}),
            "resource_constraint_fre": forms.Textarea(attrs={"rows": 5}),
            "qc_process_descr_eng": forms.Textarea(attrs={"rows": 5}),
            "qc_process_descr_fre": forms.Textarea(attrs={"rows": 5}),
            "storage_envr_notes": forms.Textarea(attrs={"rows": 5}),
            "parameters_collected_eng": forms.Textarea(attrs={"rows": 5}),
            "parameters_collected_fre": forms.Textarea(attrs={"rows": 5}),
            "additional_credit": forms.Textarea(attrs={"rows": 5}),
            "analytic_software": forms.Textarea(attrs={"rows": 5}),
            "notes": forms.Textarea(attrs={"rows": 5}),

        }

    def __init__(self, *args, **kwargs):
        SECTION_CHOICES = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch", "division",
                                                                        "name")]
        SECTION_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['section'].choices = SECTION_CHOICES


class ResourcePersonForm(forms.ModelForm):
    class Meta:
        model = models.ResourcePerson
        fields = "__all__"
        labels = {
            'notes': "Notes (optional)",
        }
        widgets = {
            'resource': forms.HiddenInput(),
            'person': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'rows': "5"}),
            # 'last_modified_by':forms.HiddenInput(),
        }


class PersonForm(forms.Form):
    LANGUAGE_CHOICES = ((None, "---"),) + models.LANGUAGE_CHOICES

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(required=False)
    position_eng = forms.CharField(label="Position title (English)", required=False)
    position_fre = forms.CharField(label="Position title (French)", required=False)
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "000-000-0000 ext.000"}), required=False)
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=False)

    field_order = ["first_name", "last_name", "email", "position_eng", "position_fre", "phone", "language",
                   "organization"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        organization_choices = [(org.id, org.name_eng) for org in models.Organization.objects.all()]
        organization_choices.insert(0, (None, "---"))

        self.fields['organization'] = forms.ChoiceField(choices=organization_choices, required=False)


class PersonCreateForm(PersonForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        # if email already exists in db
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("email address already exists in system.")
        return email


class KeywordForm(forms.ModelForm):
    class Meta:
        model = models.Keyword
        exclude = [
            'concept_scheme',
            'xml_block',
            'is_taxonomic',
        ]


class CitationForm(forms.ModelForm):
    class Meta:
        model = models.Citation
        fields = ("__all__")
        # exclude = [
        #     'concept_scheme',
        #     'xml_block',
        #     'is_taxonomic',
        # ]


class ResourceCertificationForm(forms.ModelForm):
    class Meta:
        model = models.ResourceCertification
        fields = "__all__"
        labels = {
            'notes': "Certification Notes",
        }
        widgets = {
            'certifying_user': forms.HiddenInput(),
            'resource': forms.HiddenInput(),
            'certification_date': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": 2}),
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        exclude = ["date_created", ]
        # fields = "__all__"
        # labels={
        #     'district':mark_safe("District (<a href='#' >search</a>)"),
        #     'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        # }
        widgets = {
            'resource': forms.HiddenInput(),
            # 'end_date':forms.DateInput(attrs={'type': 'date'}),
        }


class DataResourceForm(forms.ModelForm):
    class Meta:
        model = models.DataResource
        fields = "__all__"
        widgets = {
            'resource': forms.HiddenInput(),
        }


class WebServiceForm(forms.ModelForm):
    class Meta:
        model = models.WebService
        fields = "__all__"
        widgets = {
            'resource': forms.HiddenInput(),
        }


class ResourceFlagging(forms.ModelForm):
    class Meta:
        model = models.Resource
        fields = ["flagged_4_deletion", "flagged_4_publication"]

        widgets = {
            'flagged_4_deletion': forms.HiddenInput(),
            'flagged_4_publication': forms.HiddenInput(),
        }


class ReportSearchForm(forms.Form):
    REPORT_CHOICES = (
        (None, "------"),
        (1, "Batch XML export"),
        # (2, "Organizational Report / Cue Card (PDF)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    sections = forms.MultipleChoiceField(required=False, label='Region / Division / Section (Leave blank for all)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sections'].choices = [(s.id, "{}".format(s.full_name)) for s in
                                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch",
                                                                                        'division', "name")]
