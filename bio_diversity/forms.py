import inspect
from datetime import date, datetime

from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from bio_diversity.data_parsers.distributions import mactaquac_distribution_parser, coldbrook_distribution_parser
from bio_diversity.data_parsers.electrofishing import ColdbrookElectrofishingParser, MactaquacElectrofishingParser

from bio_diversity import models
from bio_diversity import utils
from bio_diversity.data_parsers.generic import GenericIndvParser, GenericGrpParser
from bio_diversity.data_parsers.picks import mactaquac_picks_parser, coldbrook_picks_parser
from bio_diversity.data_parsers.spawning import MactaquacSpawningParser, ColdbrookSpawningParser
from bio_diversity.data_parsers.tagging import ColdbrookTaggingParser, MactaquacTaggingParser
from bio_diversity.data_parsers.temperatures import temperature_parser
from bio_diversity.data_parsers.treatment import mactaquac_treatment_parser
from bio_diversity.data_parsers.water_quality import WaterQualityParser


class CreatePrams(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_date'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()


class CreateDatePrams(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_date'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()
        self.fields['start_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                  "class": "fp-date"})
        self.fields['end_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                "class": "fp-date"})

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # 1) the end date is after the start date and
        # 2) valid is false if today is after end_date
        end_date = cleaned_data.get("end_date")
        valid = cleaned_data.get("det_valid")
        if end_date:
            start_date = cleaned_data.get("start_date")
            today = date.today()
            if end_date and start_date and end_date < start_date:
                self.add_error('end_date', gettext(
                    "The end date must be after the start date!"
                ))
            elif end_date and valid and end_date < today:
                self.add_error('det_valid', gettext("Cannot be valid after end date"))

        return self.cleaned_data


class CreateTimePrams(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_date'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()
        self.fields['start_datetime'].widget = forms.HiddenInput()
        self.fields['start_datetime'].required = False
        self.fields['end_datetime'].widget = forms.HiddenInput()
        self.fields['end_datetime'].required = False
        self.fields['start_date'] = forms.DateField(widget=forms.DateInput(attrs={"placeholder": "Click to select a date...", "class": "fp-date"}))
        self.fields['end_date'] = forms.DateField(required=False, widget=forms.DateInput(attrs={"placeholder": "Click to select a date...", "class": "fp-date"}))
        self.fields['start_time'] = forms.CharField(required=False, widget=forms.DateInput(attrs={"placeholder": "Click to select a time...", "class": "fp-time"}))
        self.fields['end_time'] = forms.CharField(required=False, widget=forms.DateInput(attrs={"placeholder": "Click to select a time...", "class": "fp-time"}))

    def clean(self):
        cleaned_data = super().clean()

        if not self.is_valid():
            return cleaned_data
        # we have to make sure
        # the end datetime is after the start datetime
        # and set the datetime values
        if cleaned_data["start_time"]:
            start_time = datetime.strptime(cleaned_data["start_time"], '%H:%M').time()
        else:
            start_time = datetime.min.time()
        cleaned_data["start_datetime"] = utils.naive_to_aware(cleaned_data["start_date"], start_time)
        if cleaned_data["end_date"]:
            if cleaned_data["end_time"]:
                end_time = datetime.strptime(cleaned_data["end_time"], '%H:%M').time()
            else:
                end_time = datetime.min.time()
            cleaned_data["end_datetime"] = utils.naive_to_aware(cleaned_data["end_date"], end_time)

        end_date = cleaned_data.get("end_date")
        end_time = cleaned_data.get("end_time")
        start_time = cleaned_data.get("start_time")
        if end_date:
            start_date = cleaned_data.get("start_date")
            if end_date and start_date and end_date < start_date:
                self.add_error('end_date', gettext(
                    "The end date must be after the start date!"
                ))
            elif end_date and start_date and end_date == start_date:
                if end_time and start_time and end_time < start_time:
                    self.add_error('end_time', gettext(
                        "The end date must be after the start date!"
                    ))
        return self.cleaned_data


class AnidcForm(CreatePrams):
    class Meta:
        model = models.AnimalDetCode
        exclude = []


class AnixForm(CreatePrams):

    class Meta:
        model = models.AniDetailXref
        exclude = []
        widgets = {
            'final_contx_flag': forms.NullBooleanSelect()
        }


class AdscForm(CreatePrams):
    class Meta:
        model = models.AniDetSubjCode
        exclude = []


class CntForm(CreatePrams):
    class Meta:
        model = models.Count
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contx_id'].widget = forms.HiddenInput()


class CntcForm(CreatePrams):
    class Meta:
        model = models.CountCode
        exclude = []


class CntdForm(CreatePrams):
    class Meta:
        model = models.CountDet
        exclude = []


class CollForm(CreatePrams):
    class Meta:
        model = models.Collection
        exclude = []


class CommentKeywordsForm(forms.ModelForm):

    model = None

    class Meta:
        fields = "__all__"
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adsc_id"].queryset = models.AniDetSubjCode.objects.filter(anidc_id__name__iexact="Animal Health")


CommentKeywordsFormset = modelformset_factory(
    model=models.CommentKeywords,
    form=CommentKeywordsForm,
    extra=1,
)


class ContdcForm(CreatePrams):
    class Meta:
        model = models.ContainerDetCode
        exclude = []


class ContxForm(CreatePrams):
    class Meta:
        model = models.ContainerXRef
        exclude = []


class CdscForm(CreatePrams):
    class Meta:
        model = models.ContDetSubjCode
        exclude = []


class CupForm(CreateDatePrams):
    class Meta:
        model = models.Cup
        exclude = []


class CupdForm(CreateDatePrams):
    class Meta:
        model = models.CupDet
        exclude = []


class DataForm(CreatePrams):

    class Meta:
        model = models.DataLoader
        exclude = []

    data_types = (None, '---------')
    data_type = forms.ChoiceField(choices=data_types, label=_("Type of data entry"))
    trof_id = forms.ModelChoiceField(queryset=models.Trough.objects.all(), label="Trough")

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(DataForm, self).__init__(*args, **kwargs)

    def save(self):
        # never save this form to db
        super().save(commit=False)

    def clean(self):
        cleaned_data = super().clean()

        if not self.is_valid():
            return cleaned_data
        log_data = ""
        success = False
        parser = None
        try:
            # ----------------------------ELECTROFISHING-----------------------------------
            if cleaned_data["evntc_id"].__str__() in ["Electrofishing", "Bypass Collection", "Smolt Wheel Collection"]:
                if cleaned_data["facic_id"].__str__() == "Coldbrook":
                    parser = ColdbrookElectrofishingParser(cleaned_data)
                elif cleaned_data["facic_id"].__str__() == "Mactaquac":
                    parser = MactaquacElectrofishingParser(cleaned_data)
                log_data, success = parser.log_data, parser.success

            # -------------------------------TAGGING----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "PIT Tagging":
                if cleaned_data["facic_id"].__str__() == "Coldbrook":
                    parser = ColdbrookTaggingParser(cleaned_data)
                elif cleaned_data["facic_id"].__str__() == "Mactaquac":
                    parser = MactaquacTaggingParser(cleaned_data)
                log_data, success = parser.log_data, parser.success

            # -----------------------------MATURITY SORTING----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "Maturity Sorting":
                if cleaned_data["data_type"].__str__() == "Individual":
                    parser = GenericIndvParser(cleaned_data)
                elif cleaned_data["data_type"].__str__() == "Group":
                    parser = GenericGrpParser(cleaned_data)
                log_data = parser.log_data
                success = parser.success

            # ---------------------------WATER QUALITY----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "Water Quality Record":
                parser = WaterQualityParser(cleaned_data)
                log_data, success = parser.log_data, parser.success

            # -------------------------------SPAWNING----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "Spawning":
                if cleaned_data["facic_id"].__str__() == "Mactaquac":
                    parser = MactaquacSpawningParser(cleaned_data)
                    log_data, success = parser.log_data, parser.success
                elif cleaned_data["facic_id"].__str__() == "Coldbrook":
                    log_data, success = ColdbrookSpawningParser(cleaned_data)

            # -------------------------------TREATMENT----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "Treatment":
                if cleaned_data["facic_id"].__str__() == "Mactaquac":
                    log_data, success = mactaquac_treatment_parser(cleaned_data)

            # ---------------------------TROUGH TEMPERATURE----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "Egg Development" and\
                    cleaned_data["data_type"] == "Temperature":
                log_data, success = temperature_parser(cleaned_data)

            # ---------------------------------PICKS----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "Egg Development" and cleaned_data["data_type"] == "Picks":
                if cleaned_data["facic_id"].__str__() == "Mactaquac":
                    log_data, success = mactaquac_picks_parser(cleaned_data)
                elif cleaned_data["facic_id"].__str__() == "Coldbrook":
                    log_data, success = coldbrook_picks_parser(cleaned_data)

            # ------------------------------MEASURING----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "Measuring":
                if cleaned_data["data_type"].__str__() == "Individual":
                    parser = GenericIndvParser(cleaned_data)
                elif cleaned_data["data_type"].__str__() == "Group":
                    parser = GenericGrpParser(cleaned_data)
                log_data = parser.log_data
                success = parser.success
            # -----------------------------DISTRIBUTION----------------------------------------
            elif cleaned_data["evntc_id"].__str__() == "Distribution":
                if cleaned_data["facic_id"].__str__() == "Mactaquac":
                    log_data, success = mactaquac_distribution_parser(cleaned_data)
                elif cleaned_data["facic_id"].__str__() == "Coldbrook":
                    log_data, success = coldbrook_distribution_parser(cleaned_data)

            # -------------------------GENERAL DATA ENTRY-------------------------------------------
            else:
                parser = GenericIndvParser(cleaned_data)
                log_data = parser.log_data
                success = parser.success

        except Exception as err:
            log_data += "Error parsing data: \n"
            log_data += "\n Error: {}".format(err)

        self.request.session["log_data"] = log_data
        self.request.session["load_success"] = success


class DrawForm(CreatePrams):
    class Meta:
        model = models.Drawer
        exclude = []


class EnvForm(CreateTimePrams):
    class Meta:
        model = models.EnvCondition
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contx_id'].widget = forms.HiddenInput()


class EnvcForm(CreatePrams):
    class Meta:
        model = models.EnvCode
        exclude = []


class EnvcfForm(CreatePrams):
    class Meta:
        model = models.EnvCondFile
        exclude = []


class EnvscForm(CreatePrams):
    class Meta:
        model = models.EnvSubjCode
        exclude = []


class EnvtForm(CreatePrams):
    class Meta:
        model = models.EnvTreatment
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contx_id'].widget = forms.HiddenInput()


class EnvtcForm(CreatePrams):
    class Meta:
        model = models.EnvTreatCode
        exclude = []


class EvntForm(CreateTimePrams):
    class Meta:
        model = models.Event
        exclude = []
        widgets = {
            "evntc_id": forms.Select(attrs={"class": "chosen-select-contains"}),
            "perc_id": forms.Select(attrs={"class": "chosen-select-contains"}),
        }


class EvntcForm(CreatePrams):
    class Meta:
        model = models.EventCode
        exclude = []


class EvntfForm(CreatePrams):
    class Meta:
        model = models.EventFile
        exclude = []


class EvntfcForm(CreatePrams):
    class Meta:
        model = models.EventFileCode
        exclude = []


class FacicForm(CreatePrams):
    class Meta:
        model = models.FacilityCode
        exclude = []


class FecuForm(CreateDatePrams):
    class Meta:
        model = models.Fecundity
        exclude = []


class FeedForm(CreatePrams):
    class Meta:
        model = models.Feeding
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contx_id'].widget = forms.HiddenInput()


class FeedcForm(CreatePrams):
    class Meta:
        model = models.FeedCode
        exclude = []


class FeedmForm(CreatePrams):
    class Meta:
        model = models.FeedMethod
        exclude = []


class GrpForm(CreatePrams):
    class Meta:
        model = models.Group
        exclude = []


class GrpdForm(CreatePrams):
    class Meta:
        model = models.GroupDet
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['anix_id'].widget = forms.HiddenInput()


class HeatForm(CreatePrams):
    class Meta:
        model = models.HeathUnit
        exclude = []
        widgets = {
            'inservice_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
        }


class HeatdForm(CreateDatePrams):
    class Meta:
        model = models.HeathUnitDet
        exclude = []


class HelpTextForm(forms.ModelForm):

    model = None

    class Meta:
        fields = "__all__"
        widgets = {
            'eng_text': forms.Textarea(attrs={"rows": 2}),
            'fra_text': forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        clsmembers = [(cls[0], cls[0]) for cls in inspect.getmembers(models, inspect.isclass)]
        clsmembers.insert(0, (None, "----"))

        self.fields['model'] = forms.ChoiceField(choices=clsmembers)


HelpTextFormset = modelformset_factory(
    model=models.HelpText,
    form=HelpTextForm,
    extra=1,
)


class ImgForm(CreatePrams):
    class Meta:
        model = models.Image
        exclude = []


class ImgcForm(CreatePrams):
    class Meta:
        model = models.ImageCode
        exclude = []


class IndvForm(CreatePrams):
    class Meta:
        model = models.Individual
        exclude = []

    field_order = [
        'ufid',
        'pit_tag',
        'indv_valid',
        'grp_id',
        'spec_id',
        'stok_id',
        'coll_id',
        'comments',
    ]


class IndvdForm(CreatePrams):
    class Meta:
        model = models.IndividualDet
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['anix_id'].widget = forms.HiddenInput()


class IndvtForm(CreateTimePrams):
    class Meta:
        model = models.IndTreatment
        exclude = []
        widgets = {}


class IndvtcForm(CreatePrams):
    class Meta:
        model = models.IndTreatCode
        exclude = []


class InstForm(CreatePrams):
    class Meta:
        model = models.Instrument
        exclude = []


class InstcForm(CreatePrams):
    class Meta:
        model = models.InstrumentCode
        exclude = []


class InstdForm(CreateDatePrams):
    class Meta:
        model = models.InstrumentDet
        exclude = []


class InstdcForm(CreatePrams):
    class Meta:
        model = models.InstDetCode
        exclude = []


class LocForm(CreatePrams):
    class Meta:
        model = models.Location
        exclude = []
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loc_date'].widget = forms.HiddenInput()
        self.fields['loc_date'].required = False
        self.fields['start_date'] = forms.DateField(widget=forms.DateInput(
            attrs={"placeholder": "Click to select a date...", "class": "fp-date"}))
        self.fields['start_time'] = forms.CharField(required=False, widget=forms.DateInput(attrs={"placeholder": "Click to select a time...", "class": "fp-time"}))

    def save(self, commit=True):
        obj = super().save(commit=False)  # here the object is not commited in db
        if self.cleaned_data["start_time"]:
            start_time = datetime.strptime(self.cleaned_data["start_time"], '%H:%M').time()
        else:
            start_time = datetime.min.time()
        obj.loc_date = utils.naive_to_aware(self.cleaned_data["start_date"], start_time)
        obj.save()
        return obj


class LoccForm(CreatePrams):
    class Meta:
        model = models.LocCode
        exclude = []


class MapForm(forms.Form):
    north = forms.FloatField(required=False)
    south = forms.FloatField(required=False)
    east = forms.FloatField(required=False)
    west = forms.FloatField(required=False)
    start_date = forms.DateField(required=False, label=_("Start Date"))
    end_date = forms.DateField(required=False, label=_("End date"))
    rive_id = forms.ModelChoiceField(queryset=models.RiverCode.objects.all(), required=False, label=_("River Code"))
    subr_id = forms.ModelChoiceField(queryset=models.SubRiverCode.objects.all(), required=False, label=_("Sub River Code"))
    trib_id = forms.ModelChoiceField(queryset=models.Tributary.objects.all(), required=False, label=_("Tributary"))

    def clean(self):
        cleaned_data = super().clean()
        north = cleaned_data.get("north")
        south = cleaned_data.get("south")
        east = cleaned_data.get("east")
        west = cleaned_data.get("west")

        if not north or not south or not east or not west:
            raise forms.ValidationError("You must enter valid values for all directions.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                  "class": "fp-date"})
        self.fields['end_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                "class": "fp-date"})


class MortForm(forms.Form):
    class Meta:
        exclude = []

    gender_choices = ((None, "---------"), ('Male', 'Male'), ('Female', 'Female'), ('Immature', 'Immature'))
    mort_date = forms.DateField(required=True, label=_("Date of Mortality"))
    perc_id = forms.ModelChoiceField(required=True, queryset=models.PersonnelCode.objects.filter(perc_valid=True), label=_("Personel"))
    created_date = forms.DateField(required=True)
    created_by = forms.CharField(required=True, max_length=32)
    indv_length = forms.DecimalField(required=False, max_digits=5, label=_("Individual Length (cm)"))
    indv_mass = forms.DecimalField(required=False, max_digits=5,  label=_("Individual Mass (g)"))
    indv_vial = forms.CharField(required=False, max_length=8,  label=_("Individual Vial"))
    scale_envelope = forms.CharField(required=False, max_length=8,  label=_("Scale Envelope Label"))
    indv_gender = forms.ChoiceField(required=False, choices=gender_choices,  label=_("Individual Gender"))
    observations = forms.ModelMultipleChoiceField(required=False, queryset=models.AniDetSubjCode.objects.filter(anidc_id__name="Mortality Observation") | models.AniDetSubjCode.objects.filter(anidc_id__name="Animal Health"),  label=_("Observations"))
    indv_mort = forms.IntegerField(required=False, max_value=10000000)
    grp_mort = forms.IntegerField(required=False, max_value=10000000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_date'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()
        self.fields['indv_mort'].widget = forms.HiddenInput()
        self.fields['grp_mort'].widget = forms.HiddenInput()
        self.fields['mort_date'].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                                 "class": "fp-date"})

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["mort_date"] = utils.naive_to_aware(cleaned_data["mort_date"])

        if not self.is_valid():
            return cleaned_data

        if cleaned_data["indv_mort"]:
            indv = models.Individual.objects.filter(pk=cleaned_data["indv_mort"]).get()
            indv.indv_valid = False
            indv.save()
            cleaned_data["evnt_id"] = models.AniDetailXref.objects.filter(indv_id_id=cleaned_data["indv_mort"]).last().evnt_id
        else:
            cleaned_data["evnt_id"] = models.AniDetailXref.objects.filter(grp_id_id=cleaned_data["grp_mort"]).last().evnt_id
            grp = models.Group.objects.filter(pk=cleaned_data["grp_mort"]).get()
            indv = models.Individual(grp_id=grp,
                                     spec_id=grp.spec_id,
                                     stok_id=grp.stok_id,
                                     coll_id=grp.coll_id,
                                     indv_year=grp.grp_year,
                                     indv_valid=False,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
            indv.clean()
            indv.save()
            cleaned_data["indv_mort"] = indv.pk

        mortality_evnt, anix, mort_entered = utils.enter_mortality(indv, cleaned_data, cleaned_data["mort_date"])

        cleaned_data["evnt_id"] = mortality_evnt
        cleaned_data["facic_id"] = mortality_evnt.facic_id

        if cleaned_data["grp_mort"]:
            utils.enter_anix(cleaned_data, grp_pk=cleaned_data["grp_mort"])
            utils.enter_anix(cleaned_data, indv_pk=cleaned_data["indv_mort"], grp_pk=cleaned_data["grp_mort"])
            tank = grp.current_tank(at_date=cleaned_data["mort_date"])[0]
            contx, data_entered = utils.enter_tank_contx(tank.name, cleaned_data, grp_pk=grp.id, return_contx=True)
            utils.enter_cnt(cleaned_data, cnt_value=1, contx_pk=contx.id, cnt_code="Mortality")

        if cleaned_data["indv_length"]:
            utils.enter_indvd(anix.pk, cleaned_data, cleaned_data["mort_date"], cleaned_data["indv_length"], "Length", None)
        if cleaned_data["indv_mass"]:
            utils.enter_indvd(anix.pk, cleaned_data, cleaned_data["mort_date"], cleaned_data["indv_mass"], "Weight", None)
        if cleaned_data["indv_vial"]:
            utils.enter_indvd(anix.pk, cleaned_data, cleaned_data["mort_date"], cleaned_data["indv_vial"], "Vial", None)
        if cleaned_data["scale_envelope"]:
            utils.enter_indvd(anix.pk, cleaned_data, cleaned_data["mort_date"], cleaned_data["scale_envelope"], "Scale Envelope", None)
        if cleaned_data["indv_gender"]:
            utils.enter_indvd(anix.pk, cleaned_data, cleaned_data["mort_date"], cleaned_data["indv_gender"], "Gender", None)

        if cleaned_data["observations"].count() != 0:
            for adsc in cleaned_data["observations"]:
                utils.enter_indvd(anix.pk, cleaned_data, cleaned_data["mort_date"], None, adsc.anidc_id.name, adsc.name, None)


class OrgaForm(CreatePrams):
    class Meta:
        model = models.Organization
        exclude = []


class PairForm(CreateDatePrams):
    class Meta:
        model = models.Pairing
        exclude = []
        widgets = {
            "indv_id": forms.Select(attrs={"class": "chosen-select-contains"}),
        }


class PercForm(CreatePrams):
    class Meta:
        model = models.PersonnelCode
        exclude = []


class PrioForm(CreatePrams):
    class Meta:
        model = models.PriorityCode
        exclude = []


class ProgForm(CreateDatePrams):
    class Meta:
        model = models.Program
        exclude = []


class ProgaForm(CreatePrams):
    class Meta:
        model = models.ProgAuthority
        exclude = []


class ProtForm(CreateDatePrams):
    class Meta:
        model = models.Protocol
        exclude = []
        widgets = {
            "evntc_id": forms.Select(attrs={"class": "chosen-select-contains"}),
            "protc_id": forms.Select(attrs={"class": "chosen-select-contains"}),
        }


class ProtcForm(CreatePrams):
    class Meta:
        model = models.ProtoCode
        exclude = []


class ProtfForm(CreatePrams):
    class Meta:
        model = models.Protofile
        exclude = []


class QualForm(CreatePrams):
    class Meta:
        model = models.QualCode
        exclude = []


class RelcForm(CreatePrams):
    class Meta:
        model = models.ReleaseSiteCode
        exclude = []


class ReportForm(forms.Form):
    class Meta:
        model = models.ReleaseSiteCode
        exclude = []

    REPORT_CHOICES = (
        (None, "------"),
        (1, "Facility Tanks Report (xlsx)"),
        (2, "River Code Report Report (xlsx)"),
    )
    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    facic_id = forms.ModelChoiceField(required=False,
                                      queryset=models.FacilityCode.objects.all(),
                                      label=_("Facility"))
    stok_id = forms.ModelChoiceField(required=False,
                                     queryset=models.StockCode.objects.all(),
                                     label=_("Stock Code"))
    on_date = forms.DateField(required=False, label=_("Report Date"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["on_date"].widget = forms.DateInput(attrs={"placeholder": "Click to select a date..",
                                                               "class": "fp-date"})


class RiveForm(CreatePrams):
    class Meta:
        model = models.RiverCode
        exclude = []


class RoleForm(CreatePrams):
    class Meta:
        model = models.RoleCode
        exclude = []


class SampForm(CreatePrams):
    class Meta:
        model = models.Sample
        exclude = []


class SampcForm(CreatePrams):
    class Meta:
        model = models.SampleCode
        exclude = []


class SampdForm(CreatePrams):
    class Meta:
        model = models.SampleDet
        exclude = []


class SireForm(CreatePrams):
    class Meta:
        model = models.Sire
        exclude = []
        widgets = {
            "indv_id": forms.Select(attrs={"class": "chosen-select-contains"}),
        }


class SpwndForm(CreatePrams):
    class Meta:
        model = models.SpawnDet
        exclude = []


class SpwndcForm(CreatePrams):
    class Meta:
        model = models.SpawnDetCode
        exclude = []


class SpwnscForm(CreatePrams):
    class Meta:
        model = models.SpawnDetSubjCode
        exclude = []


class SpecForm(CreatePrams):
    class Meta:
        model = models.SpeciesCode
        exclude = []


class StokForm(CreatePrams):
    class Meta:
        model = models.StockCode
        exclude = []


class SubrForm(CreatePrams):
    class Meta:
        model = models.SubRiverCode
        exclude = []


class TankForm(CreatePrams):
    class Meta:
        model = models.Tank
        exclude = []
        # to set the ordering:
        fields = ['name', 'nom', 'facic_id', 'description_en', 'description_fr', 'created_date', 'created_by']


class TankdForm(CreateDatePrams):
    class Meta:
        model = models.TankDet
        exclude = []


class TeamForm(CreatePrams):
    class Meta:
        model = models.TeamXRef
        exclude = []


class TrayForm(CreateDatePrams):
    class Meta:
        model = models.Tray
        exclude = []


class TraydForm(CreateDatePrams):
    class Meta:
        model = models.TrayDet
        exclude = []


class TribForm(CreatePrams):
    class Meta:
        model = models.Tributary
        exclude = []


class TrofForm(CreatePrams):
    class Meta:
        model = models.Trough
        exclude = []


class TrofdForm(CreateDatePrams):
    class Meta:
        model = models.TroughDet
        exclude = []


class UnitForm(CreatePrams):
    class Meta:
        model = models.UnitCode
        exclude = []
