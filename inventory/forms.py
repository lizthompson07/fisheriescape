from django import forms
from django.core import validators
from . import models


class ResourceCreateForm(forms.ModelForm):
    add_custodian = forms.BooleanField(required=False, label="Add yourself as custodian")
    add_point_of_contact = forms.BooleanField(required=False, label="Add Regional Data Manager as a Point of Contact")
    class Meta:
        model = models.Resource
        exclude = [
            'file_identifier',
            'uuid',
            'date_verified',
            'date_last_modified',
            'fgp_publication_date',
            'citations',
            'keywords',
            'people',
            'flagged_4_publication',
            'flagged_4_deletion',
        ]
        widgets = {
            'last_modified_by':forms.HiddenInput(),
            'title_eng':forms.Textarea(attrs={"rows":5}),
            'title_fre':forms.Textarea(attrs={"rows":5}),
            "purpose_eng":forms.Textarea(attrs={"rows":5}),
            "purpose_fre":forms.Textarea(attrs={"rows":5}),
            "descr_eng":forms.Textarea(attrs={"rows":8}),
            "descr_fre":forms.Textarea(attrs={"rows":8}),
            "physical_sample_descr_eng":forms.Textarea(attrs={"rows":5}),
            "physical_sample_descr_fre":forms.Textarea(attrs={"rows":5}),
            "sampling_method_eng":forms.Textarea(attrs={"rows":5}),
            "sampling_method_fre":forms.Textarea(attrs={"rows":5}),
            "resource_constraint_eng":forms.Textarea(attrs={"rows":5}),
            "resource_constraint_fre":forms.Textarea(attrs={"rows":5}),
            "qc_process_descr_eng":forms.Textarea(attrs={"rows":5}),
            "qc_process_descr_fre":forms.Textarea(attrs={"rows":5}),
            "storage_envr_notes":forms.Textarea(attrs={"rows":5}),
            "parameters_collected_eng":forms.Textarea(attrs={"rows":5}),
            "parameters_collected_fre":forms.Textarea(attrs={"rows":5}),
            "additional_credit":forms.Textarea(attrs={"rows":5}),
            "analytic_software":forms.Textarea(attrs={"rows":5}),
            "notes":forms.Textarea(attrs={"rows":5}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = models.Resource
        exclude = [
            'file_identifier',
            'uuid',
            'date_verified',
            'date_last_modified',
            # 'fgp_publication_date',
            'citations',
            'keywords',
            'people',
            'flagged_4_publication',
            'flagged_4_deletion',
        ]
        widgets = {
            'last_modified_by':forms.HiddenInput(),
            'title_eng':forms.Textarea(attrs={"rows":5}),
            'title_fre':forms.Textarea(attrs={"rows":5}),
            "purpose_eng":forms.Textarea(attrs={"rows":5}),
            "purpose_fre":forms.Textarea(attrs={"rows":5}),
            "descr_eng":forms.Textarea(attrs={"rows":8}),
            "descr_fre":forms.Textarea(attrs={"rows":8}),
            "physical_sample_descr_eng":forms.Textarea(attrs={"rows":5}),
            "physical_sample_descr_fre":forms.Textarea(attrs={"rows":5}),
            "sampling_method_eng":forms.Textarea(attrs={"rows":5}),
            "sampling_method_fre":forms.Textarea(attrs={"rows":5}),
            "resource_constraint_eng":forms.Textarea(attrs={"rows":5}),
            "resource_constraint_fre":forms.Textarea(attrs={"rows":5}),
            "qc_process_descr_eng":forms.Textarea(attrs={"rows":5}),
            "qc_process_descr_fre":forms.Textarea(attrs={"rows":5}),
            "storage_envr_notes":forms.Textarea(attrs={"rows":5}),
            "parameters_collected_eng":forms.Textarea(attrs={"rows":5}),
            "parameters_collected_fre":forms.Textarea(attrs={"rows":5}),
            "additional_credit":forms.Textarea(attrs={"rows":5}),
            "analytic_software":forms.Textarea(attrs={"rows":5}),
            "notes":forms.Textarea(attrs={"rows":5}),

        }

class ResourcePersonForm(forms.ModelForm):
    class Meta:
        model = models.ResourcePerson
        fields = "__all__"
        labels={
            'notes':"Notes (optional)",
            'longitude_w':"Longitude",
        }
        widgets = {
            'resource':forms.HiddenInput(),
            'person':forms.HiddenInput(),
            'notes':forms.Textarea(attrs={'rows':"5"}),
            # 'last_modified_by':forms.HiddenInput(),
        }



class PersonCreateForm(forms.Form):

    LANGUAGE_CHOICES = ((None,"---"),) + models.LANGUAGE_CHOICES

    ORGANIZATION_CHOICES = ((None,"---"),)
    for org in models.Organization.objects.all():
        ORGANIZATION_CHOICES = ORGANIZATION_CHOICES.__add__(((org.id,org.name_eng),))

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(required=False)
    position_eng = forms.CharField(label="Position title (English)",required=False)
    position_fre = forms.CharField(label="Position title (French)",required=False)
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"000-000-0000 ext.000"}),required=False)
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES,required=False)
    organization = forms.ChoiceField(choices=ORGANIZATION_CHOICES,required=False)


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
        labels={
            'notes':"Certification Notes",
        }
        widgets = {
            'certifying_user': forms.HiddenInput(),
            'resource': forms.HiddenInput(),
            'certification_date': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows":2}),
        }

class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        exclude = ["date_created",]
        # fields = "__all__"
        # labels={
        #     'district':mark_safe("District (<a href='#' >search</a>)"),
        #     'vessel':mark_safe("Vessel CFVN (<a href='#' >add</a>)"),
        # }
        widgets = {
            'resource':forms.HiddenInput(),
            # 'end_date':forms.DateInput(attrs={'type': 'date'}),
        }

class DataResourceForm(forms.ModelForm):
    class Meta:
        model = models.DataResource
        fields = "__all__"
        widgets = {
            'resource':forms.HiddenInput(),
        }

class WebServiceForm(forms.ModelForm):
    class Meta:
        model = models.WebService
        fields = "__all__"
        widgets = {
            'resource':forms.HiddenInput(),
        }



class ResourceFlagging(forms.ModelForm):
    class Meta:
        model = models.Resource
        fields = ["flagged_4_deletion","flagged_4_publication"]

        widgets = {
            'flagged_4_deletion':forms.HiddenInput(),
            'flagged_4_publication':forms.HiddenInput(),
        }
