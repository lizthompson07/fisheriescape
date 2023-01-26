from django import forms
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy

from shared_models import models as shared_models
from . import models
from .data_fixtures import resource_types, statuses

chosen_js = {"class": "chosen-select-contains"}
attr_fp_date_time = {"class": "fp-date-time", "placeholder": "Select Date and Time.."}
attr_fp_date = {"class": "fp-date", "placeholder": "Select a Date.."}


class ResourceForm(forms.ModelForm):
    add_custodian = forms.BooleanField(required=False, label="Add yourself as custodian")

    class Meta:
        model = models.Resource
        exclude = [
            'file_identifier',
            'uuid',
            'date_verified',
            'citations2',
            'keywords',
            'people',
            'flagged_4_publication',
            'flagged_4_deletion',
            'completedness_rating',
            'completedness_report',
            'translation_needed',
            'paa_items'
        ]
        widgets = {
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
            "distribution_formats": forms.SelectMultiple(attrs=chosen_js),
            "parameters_collected_fre": forms.Textarea(attrs={"rows": 5}),
            "additional_credit": forms.Textarea(attrs={"rows": 5}),
            "analytic_software": forms.Textarea(attrs={"rows": 5}),
            "notes": forms.Textarea(attrs={"rows": 5}),
            "fgp_publication_date": forms.DateInput(attrs=attr_fp_date),
            "od_publication_date": forms.DateInput(attrs=attr_fp_date),
            "od_release_date": forms.DateInput(attrs=attr_fp_date),
            "last_revision_date": forms.DateInput(attrs=attr_fp_date),
            "parent": forms.Select(attrs=chosen_js),
        }
        labels = {
            "section": "DFO Section",
            "parent": _("Parent Resource"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["time_start_month"].label += _(" (optional)")
        self.fields["time_start_day"].label += _(" (optional)")
        self.fields["time_end_year"].label += _(" (optional)")
        self.fields["time_end_month"].label += _(" (optional)")
        self.fields["time_end_day"].label += _(" (optional)")

        SECTION_CHOICES = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch", "division",
                                                                        "name")]
        SECTION_CHOICES.insert(0, tuple((None, "---")))

        self.fields['section'].choices = SECTION_CHOICES
        self.fields['section'].widget.attrs = chosen_js

        resource_type_choices = [(obj.id, "{}  ({})".format(obj.label, obj.notes) if obj.notes else "{}".format(obj.label)) for obj in
                                 resource_types.get_instances()]
        resource_type_choices.insert(0, tuple((None, "---")))

        status_choices = [(obj.id, "{}  ({})".format(obj.label, obj.notes) if obj.notes else "{}".format(obj.label)) for obj in
                          statuses.get_instances()]
        status_choices.insert(0, tuple((None, "---")))
        self.fields['resource_type'].choices = resource_type_choices
        self.fields['status'].choices = status_choices

        if kwargs.get("instance"):
            del self.fields["add_custodian"]

        if kwargs.get("initial") and kwargs.get("initial").get("cloning"):
            # m2m
            del self.fields["distribution_formats"]
            # non-cloning fields
            del self.fields["odi_id"]
            del self.fields["public_url"]
            del self.fields["fgp_publication_date"]
            del self.fields["od_publication_date"]
            del self.fields["od_release_date"]
            del self.fields["last_revision_date"]


class ResourceKeywordForm(forms.ModelForm):
    class Meta:
        model = models.Resource
        fields = [
            'keywords',
        ]
        widgets = {
            "keywords": forms.SelectMultiple(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        keyword_choices = []
        for obj in models.Keyword.objects.all().order_by("keyword_domain", "text_value_eng"):
            if obj.keyword_domain_id == 8:
                keyword_choices.append(
                    (obj.id, "[{}] {}".format("ISO Topic Category", obj.text_value_eng))
                )
            elif obj.keyword_domain_id == 6:
                keyword_choices.append(
                    (obj.id, "[{}] {}".format("Core Subject", obj.text_value_eng))
                )
            elif obj.keyword_domain_id == 7:
                keyword_choices.append(
                    (obj.id, "[{}] {}".format("DFO Area", obj.text_value_eng))
                )
            elif obj.is_taxonomic:
                keyword_choices.append(
                    (obj.id, mark_safe("[{}] <em>{}</em> | {}".format("Taxonomic", obj.text_value_eng, obj.details)))
                )
            else:
                keyword_choices.append(
                    (obj.id, "[{}] {}".format("General", obj.text_value_eng))
                )
            # context['kcount_tc'] = self.object.keywords.filter(keyword_domain_id__exact=8).count()
            # context['kcount_cst'] = self.object.keywords.filter(keyword_domain_id__exact=6).count()
            # context['kcount_tax'] = self.object.keywords.filter(is_taxonomic__exact=True).count()
            # context['kcount_loc'] = self.object.keywords.filter(keyword_domain_id__exact=7).count()

            # context['kcount_other'] = self.object.keywords.filter(
            #     ~Q(keyword_domain_id=8) & ~Q(keyword_domain_id=6) & ~Q(keyword_domain_id=7) & Q(is_taxonomic=False)).count()
            #
            # topic
            # cat
            # core
            # sub
            # taxonoimic
            # dfo
            # area
            # other
            #
        self.fields["keywords"].choices = keyword_choices


class ResourcePersonForm(forms.ModelForm):
    class Meta:
        model = models.ResourcePerson2
        fields = "__all__"
        labels = {
            'notes': "Additional description of role (optional)",
            'roles': "Please select all roles for this person",
        }
        widgets = {
            'notes': forms.Textarea(attrs={'rows': "5"}),
            'roles': forms.SelectMultiple(attrs=chosen_js),
            'user': forms.Select(attrs=chosen_js),
            'organization': forms.Select(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        role_choices = [(r.id, "{} - {}".format(r.role, r.notes)) for r in models.PersonRole.objects.all()]
        role_choices.insert(0, (None, "-----"))
        self.fields['roles'].choices = role_choices
        if kwargs.get("instance"):
            del self.fields["user"]


class PersonForm(forms.Form):
    LANGUAGE_CHOICES = ((None, "---"),) + models.LANGUAGE_CHOICES

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(required=True)
    position_eng = forms.CharField(label="Position title (English)", required=False)
    position_fre = forms.CharField(label="Position title (French)", required=False)
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "000-000-0000 ext.000"}), required=False)
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=False)
    organization = forms.ModelChoiceField(required=False, queryset=models.Organization.objects.all())

    field_order = ["first_name", "last_name", "email", "position_eng", "position_fre", "phone", "language",
                   "organization"]


class PersonCreateForm(PersonForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        # if email already exists in db
        if User.objects.filter(email__iexact=email).count() > 0:
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
        model = shared_models.Citation
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
            'notes': "Certification notes (mandatory)",
        }
        widgets = {
            'notes': forms.Textarea(attrs={"rows": 2}),
        }


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        exclude = ["date_created", ]


class DataResourceForm(forms.ModelForm):
    class Meta:
        model = models.DataResource
        fields = "__all__"


class WebServiceForm(forms.ModelForm):
    class Meta:
        model = models.WebService
        fields = "__all__"


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
        (2, "Open Data Inventory - Quarterly Report"),
        (3, "Physical Collections Report (xlsx)"),
        (4, "Resources Report (xlsx)"),
        (5, "Resource published to Open Data"),
        (6, "Data Custodian Report (xlsx)"),
        (7, "Data Management Agreements (xlsx)"),
    )

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    sections = forms.MultipleChoiceField(required=False, label='Section (Leave blank for all)',
                                         widget=forms.SelectMultiple(attrs=chosen_js))
    regions = forms.MultipleChoiceField(required=False, label='Regions (Leave blank for all)', widget=forms.SelectMultiple(attrs=chosen_js))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sections'].choices = [(s.id, "{}".format(s.full_name)) for s in
                                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch",
                                                                                        'division', "name")]
        self.fields['regions'].choices = [(r.id, "{}".format(r)) for r in shared_models.Region.objects.all()]


class TempForm(forms.ModelForm):
    class Meta:
        model = models.Resource
        fields = ["title_eng", "section", "status", "descr_eng", "purpose_eng"]
        widgets = {
            'section': forms.Select(attrs=chosen_js),
            # 'tags': forms.SelectMultiple(attrs=chosen_js),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SECTION_CHOICES = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch", "division", "name")]
        SECTION_CHOICES.insert(0, tuple((None, "---")))

        self.fields['section'].choices = SECTION_CHOICES


TempFormSet = modelformset_factory(
    model=models.Resource,
    form=TempForm,
    extra=0,
)


class InventoryUserForm(forms.ModelForm):
    class Meta:
        model = models.InventoryUser
        fields = "__all__"
        widgets = {
            'user': forms.Select(attrs=chosen_js),
        }


InventoryUserFormset = modelformset_factory(
    model=models.InventoryUser,
    form=InventoryUserForm,
    extra=1,
)


class DMAForm(forms.ModelForm):
    class Meta:
        model = models.DMA
        exclude = ["project"]
        widgets = {
            'storage_solutions': forms.SelectMultiple(attrs=chosen_js),
            'data_contact': forms.Select(attrs=chosen_js),
            'metadata_contact': forms.Select(attrs=chosen_js),
            'section': forms.Select(attrs=chosen_js),
            'resource': forms.Select(attrs=chosen_js),
        }
        labels = {
            "resource": gettext_lazy("Is there an associated record in the DM Apps Science Data Inventory?")
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        section_choices = [(s.id, s.full_name) for s in
                           shared_models.Section.objects.all().order_by("division__branch__region", "division__branch", "division", "name")]
        section_choices.insert(0, tuple((None, "-------")))
        self.fields['section'].choices = section_choices

        resource_choices = [(r.id, f"{r.t_title} ({r.uuid})") for r in models.Resource.objects.all().order_by(_("title_eng"))]
        resource_choices.insert(0, tuple((None, "-------")))
        self.fields['resource'].choices = resource_choices


class DMAReviewForm(forms.ModelForm):
    class Meta:
        model = models.DMAReview
        exclude = ["dma"]
