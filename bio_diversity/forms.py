import inspect
import math
from datetime import date, datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import modelformset_factory
from django.utils.translation import gettext
import pandas as pd

from bio_diversity import models
from bio_diversity.utils import comment_parser


class CreatePrams(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_date'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()
        # forms.DateInput(attrs={"placeholder": "Click to select a date..",
        #                       "class": "fp-date"})


class CreateTimePrams(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['created_date'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()
        # forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
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


class AnidcForm(CreatePrams):
    class Meta:
        model = models.AnimalDetCode
        exclude = []


class AnixForm(CreatePrams):
    class Meta:
        model = models.AniDetailXref
        exclude = []


class AdscForm(CreatePrams):
    class Meta:
        model = models.AniDetSubjCode
        exclude = []


class CntForm(CreatePrams):
    class Meta:
        model = models.Count
        exclude = []


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


class CupForm(CreatePrams):
    class Meta:
        model = models.Cup
        exclude = []


class CupdForm(CreateTimePrams):
    class Meta:
        model = models.CupDet
        exclude = []


class DataForm(CreatePrams):

    class Meta:
        model = models.DataLoader
        exclude = []

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(DataForm, self).__init__(*args, **kwargs)

    def save(self):
        # never save this form to db
        super().save(commit=False)

    def clean(self):
        cleaned_data = super().clean()

        log_data = "Loading Data Results: \n"
        rows_parsed = 0
        rows_entered = 0

        # --------------------------ELECTROFISHING DATA ENTRY-----------------------------------
        if cleaned_data["evntc_id"].__str__() == "Electrofishing" and cleaned_data["facic_id"].__str__() == "Coldbrook":
            try:
                data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl')
                data_dict = data.to_dict('records')
            except Exception as err:
                raise Exception("File format not valid: {}".format(err.__str__()))
            parsed = True

            self.request.session["load_success"] = True
            for row in data_dict:
                row_parsed = True
                row_entered = True
                try:
                    loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                                          locc_id_id=1,
                                          rive_id=models.RiverCode.objects.filter(name=row["River"]).get(),
                                          subr_id=models.SubRiverCode.objects.filter(name__iexact=row["Branch"]).get(),
                                          relc_id=models.ReleaseSiteCode.objects.filter(name__iexact=row["Site"]).get(),
                                          loc_date=datetime.strptime(row["Date"], "%Y-%b-%d"),
                                          comments=row["Comments"],
                                          created_by=cleaned_data["created_by"],
                                          created_date=cleaned_data["created_date"],
                                          )
                    try:
                        loc.clean()
                        loc.save()
                    except ValidationError:
                        row_entered = False
                        loc = models.Location.objects.filter(evnt_id=loc.evnt_id, locc_id=loc.locc_id,
                                                             rive_id=loc.rive_id, subr_id=loc.subr_id,
                                                             relc_id=loc.relc_id, loc_date=loc.loc_date).get()

                    if not math.isnan(row["temp"]):
                        env = models.EnvCondition(loc_id_id=loc.pk,
                                                  inst_id=models.Instrument.objects.first(),
                                                  envc_id=models.EnvCode.objects.filter(name__iexact="Temperature").get(),
                                                  env_val=row["temp"],
                                                  env_start=datetime.strptime(row["Date"], "%Y-%b-%d"),
                                                  env_avg=False,
                                                  qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                  created_by=cleaned_data["created_by"],
                                                  created_date=cleaned_data["created_date"],
                                                  )
                        try:
                            env.clean()
                            env.save()
                        except ValidationError:
                            row_entered = False
                            pass
                    if not math.isnan(row["# of salmon observed/collected"]):
                        cnt = models.Count(loc_id_id=loc.pk,
                                           spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                           cntc_id=models.CountCode.objects.filter(name__iexact="Fish Caught").get(),
                                           cnt=row["# of salmon observed/collected"],
                                           est=False,
                                           created_by=cleaned_data["created_by"],
                                           created_date=cleaned_data["created_date"],
                                           )
                        try:
                            cnt.clean()
                            cnt.save()
                        except ValidationError:
                            row_entered = False
                            pass
                except Exception as err:
                    row_parsed = False
                    parsed = False
                    self.request.session["load_success"] = False
                    log_data += "Error parsing row: \n"
                    log_data += str(row)
                    log_data += "\n Error: {}".format(err.__str__())
                    break
                if row_entered:
                    rows_entered += 1
                    rows_parsed += 1
                elif row_parsed:
                    rows_parsed += 1
            if parsed:
                try:
                    grp = models.Group(spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                       stok_id=models.StockCode.objects.filter(name=data["River"][0]).get(),
                                       coll_id=models.Collection.objects.filter(name__icontains=data["purpose"][0][:8]).get(),
                                       grp_valid=True,
                                       created_by=cleaned_data["created_by"],
                                       created_date=cleaned_data["created_date"],
                                       )
                    try:
                        grp.clean()
                        grp.save()
                    except ValidationError:
                        grp = models.Group.objects.filter(spec_id=grp.spec_id, stok_id=grp.stok_id,
                                                          coll_id=grp.coll_id).get()
                    anix = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                grp_id_id=grp.pk,
                                                created_by=cleaned_data["created_by"],
                                                created_date=cleaned_data["created_date"],
                                                )
                    try:
                        anix.clean()
                        anix.save()
                    except ValidationError:
                        pass
                    grpd = models.GroupDet(anix_id_id=anix.pk,
                                           anidc_id=models.AnimalDetCode.objects.filter(name__iexact="Number of Fish").get(),
                                           det_val=data["# of salmon observed/collected"].sum(),
                                           qual_id=models.QualCode.objects.filter(name="Good").get(),
                                           # det_val=True,
                                           created_by=cleaned_data["created_by"],
                                           created_date=cleaned_data["created_date"],
                                           )
                    try:
                        grpd.clean()
                        grpd.save()
                    except ValidationError:
                        pass
                except Exception as err:
                    log_data += "Error parsing common data: \n"
                    log_data += "\n Error: {}".format(err.__str__())
                    self.request.session["load_success"] = False
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to" \
                        " database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))

        # ---------------------------TAGGING DATA ENTRY----------------------------------------
        elif cleaned_data["evntc_id"].__str__() == "Tagging" and cleaned_data["facic_id"].__str__() == "Coldbrook":
            try:
                data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                                     converters={'to tank': str})
                data_dict = data.to_dict('records')
            except Exception as err:
                raise Exception("File format not valid: {}".format(err.__str__()))
            parsed = True
            self.request.session["load_success"] = True
            try:
                grp_id = models.Group.objects.filter(stok_id__name=data_dict[0]["Stock"],
                                                     coll_id__name=data_dict[0]["Group"]).get().pk
            except Exception as err:
                log_data += "Error finding origin group (check first row): \n"
                log_data += "Error: {}\n\n".format(err.__str__())
                self.request.session["load_success"] = False

            for row in data_dict:
                row_parsed = True
                row_entered = False
                try:
                    indv = models.Individual(grp_id_id=grp_id,
                                             spec_id_id=1,
                                             stok_id=models.StockCode.objects.filter(name=row["Stock"]).get(),
                                             coll_id=models.Collection.objects.filter(name__iexact=row["Group"].strip()).get(),
                                             ufid=row["Universal Fish ID"],
                                             pit_tag=row["PIT tag"],
                                             indv_valid=True,
                                             comments=row["comments"],
                                             created_by=cleaned_data["created_by"],
                                             created_date=cleaned_data["created_date"],
                                             )
                    try:
                        indv.clean()
                        indv.save()
                    except (ValidationError, IntegrityError):
                        indv = models.Individual.objects.filter(ufid=indv.ufid, pit_tag=indv.pit_tag).get()

                    if not row["to tank"] == "nan":
                        contx_to = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                        tank_id=models.Tank.objects.filter(name=row["to tank"]).get(),
                                                        created_by=cleaned_data["created_by"],
                                                        created_date=cleaned_data["created_date"],
                                                        )
                        try:
                            contx_to.clean()
                            contx_to.save()
                        except ValidationError:
                            contx_to = models.ContainerXRef.objects.filter(evnt_id=contx_to.evnt_id,
                                                                           tank_id=contx_to.tank_id).get()

                        anix_to = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                       indv_id_id=indv.pk,
                                                       contx_id_id=contx_to.pk,
                                                       created_by=cleaned_data["created_by"],
                                                       created_date=cleaned_data["created_date"],
                                                       )
                        try:
                            anix_to.clean()
                            anix_to.save()
                        except ValidationError:
                            pass

                    anix_indv = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                     indv_id_id=indv.pk,
                                                     created_by=cleaned_data["created_by"],
                                                     created_date=cleaned_data["created_date"],
                                                     )
                    try:
                        anix_indv.clean()
                        anix_indv.save()
                    except ValidationError:
                        anix_indv = models.AniDetailXref.objects.filter(evnt_id=anix_indv.evnt_id,
                                                                        indv_id=anix_indv.indv_id,
                                                                        contx_id__isnull=True,
                                                                        loc_id__isnull=True,
                                                                        spwn_id__isnull=True,
                                                                        grp_id__isnull=True,
                                                                        indvt_id__isnull=True,
                                                                        ).get()

                    anix_grp = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                    indv_id_id=indv.pk,
                                                    grp_id_id=grp_id,
                                                    created_by=cleaned_data["created_by"],
                                                    created_date=cleaned_data["created_date"],
                                                    )
                    try:
                        anix_grp.clean()
                        anix_grp.save()
                        row_entered = True
                    except ValidationError:
                        row_entered = False

                    if not math.isnan(row["Length (cm)"]):
                        indvd_length = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                            anidc_id=models.AnimalDetCode.objects.filter(name="Length").get(),
                                                            det_val=row["Length (cm)"],
                                                            qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                            created_by=cleaned_data["created_by"],
                                                            created_date=cleaned_data["created_date"],
                                                            )
                        try:
                            indvd_length.clean()
                            indvd_length.save()
                            row_entered = True
                        except ValidationError:
                            row_entered = False
                    if not math.isnan(row["Weight (g)"]):
                        indvd_mass = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                          anidc_id=models.AnimalDetCode.objects.filter(name="Weight").get(),
                                                          det_val=row["Weight (g)"],
                                                          qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                          created_by=cleaned_data["created_by"],
                                                          created_date=cleaned_data["created_date"],
                                                          )
                        try:
                            indvd_mass.clean()
                            indvd_mass.save()
                            row_entered = True
                        except ValidationError:
                            row_entered = False
                except Exception as err:
                    row_parsed = False
                    parsed = False
                    self.request.session["load_success"] = False
                    log_data += "Error parsing row: \n"
                    log_data += str(row)
                    log_data += "\n Error: {}".format(err.__str__())
                    break
                if row_entered:
                    rows_entered += 1
                    rows_parsed += 1
                elif row_parsed:
                    rows_parsed += 1
            if not parsed:
                self.request.session["load_success"] = False
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))

        # ---------------------------MATURITY SORTING DATA ENTRY----------------------------------------
        elif cleaned_data["evntc_id"].__str__() == "Maturity Sorting" and cleaned_data["facic_id"].__str__() == "Mactaquac":
            try:
                data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                                     converters={'PIT': str})
                data["COMMENTS"] = data["COMMENTS"].fillna('')
                data_dict = data.to_dict('records')
            except Exception as err:
                raise Exception("File format not valid: {}".format(err.__str__()))
            parsed = True
            self.request.session["load_success"] = True
            sex_dict = {"M": "Male",
                        "F": "Female",
                        "I": "Immature"}
            for row in data_dict:
                row_parsed = True
                row_entered = False
                try:
                    indv_qs = models.Individual.objects.filter(pit_tag=row["PIT"])
                    if len(indv_qs) == 1:
                        indv = indv_qs.get()
                    else:
                        row_entered = False
                        row_parsed = False
                        indv = False
                        log_data += "Fish with PIT {} not found in db".format(row["PIT"])

                    if indv:
                        anix_indv = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                         indv_id_id=indv.pk,
                                                         created_by=cleaned_data["created_by"],
                                                         created_date=cleaned_data["created_date"],
                                                         )
                        try:
                            anix_indv.clean()
                            anix_indv.save()
                        except ValidationError:
                            anix_indv = models.AniDetailXref.objects.filter(evnt_id=anix_indv.evnt_id,
                                                                            indv_id=anix_indv.indv_id,
                                                                            contx_id__isnull=True,
                                                                            loc_id__isnull=True,
                                                                            spwn_id__isnull=True,
                                                                            grp_id__isnull=True,
                                                                            indvt_id__isnull=True,
                                                                            ).get()
                        if row["SEX"]:
                            indvd_sex = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                             anidc_id=models.AnimalDetCode.objects.filter(
                                                                 name="Gender").get(),
                                                             adsc_id=models.AniDetSubjCode.objects.filter(
                                                                 name=sex_dict[row["SEX"]]).get(),
                                                             qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                             comments=row["COMMENTS"],
                                                             created_by=cleaned_data["created_by"],
                                                             created_date=cleaned_data["created_date"],
                                                             )
                            try:
                                indvd_sex.clean()
                                indvd_sex.save()
                            except (ValidationError, IntegrityError) as e:
                                pass
                        if row["ORIGIN POND"]:
                            contx_to = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                            tank_id=models.Tank.objects.filter(name=row["ORIGIN POND"]).get(),
                                                            created_by=cleaned_data["created_by"],
                                                            created_date=cleaned_data["created_date"],
                                                            )
                            try:
                                contx_to.clean()
                                contx_to.save()
                            except ValidationError:
                                row_entered = False
                                contx_to = models.ContainerXRef.objects.filter(evnt_id=contx_to.evnt_id,
                                                                               tank_id=contx_to.tank_id).get()

                            anix_contx = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                              indv_id_id=indv.pk,
                                                              contx_id=contx_to,
                                                              created_by=cleaned_data["created_by"],
                                                              created_date=cleaned_data["created_date"],
                                                              )
                            try:
                                anix_contx.clean()
                                anix_contx.save()
                                row_entered = True
                            except ValidationError:
                                row_entered = False
                        if row["COMMENTS"]:
                            comment_parser(row["COMMENTS"], anix_indv)
                    else:
                        break

                except Exception as err:
                    parsed = False
                    self.request.session["load_success"] = False
                    log_data += "Error parsing row: \n"
                    log_data += str(row)
                    log_data += "\n Error: {}".format(err.__str__())
                    break
                if row_entered:
                    rows_entered += 1
                    rows_parsed += 1
                elif row_parsed:
                    rows_parsed += 1
            if not parsed:
                self.request.session["load_success"] = False
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
        else:
            log_data = "Data loading not set up for this event type.  No data loaded."
        self.request.session["log_data"] = log_data


class DrawForm(CreatePrams):
    class Meta:
        model = models.Drawer
        exclude = []


class EnvForm(CreatePrams):
    class Meta:
        model = models.EnvCondition
        exclude = []
        widgets = {
            'env_start': forms.DateTimeInput(attrs={"placeholder": "Click to select a date...",
                                                    "class": "fp-date-time"}),
            'env_end': forms.DateTimeInput(attrs={"placeholder": "Click to select a date...", "class": "fp-date-time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # 1) the end date is after the start date and
        end_date = cleaned_data.get("env_end")
        if end_date:
            start_date = cleaned_data.get("env_start")
            if end_date and start_date and end_date < start_date:
                self.add_error('env_end', gettext(
                    "The end date must be after the start date!"
                ))


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


class EnvtcForm(CreatePrams):
    class Meta:
        model = models.EnvTreatCode
        exclude = []


class EvntForm(CreatePrams):
    class Meta:
        model = models.Event
        exclude = []
        widgets = {
            'evnt_start': forms.DateTimeInput(attrs={"placeholder": "Click to select a date...",
                                                     "class": "fp-date-time"}),
            'evnt_end': forms.DateTimeInput(attrs={"placeholder": "Click to select a date...",
                                                   "class": "fp-date-time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['team_id'].create_url = 'bio_diversity:create_team'

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # 1) the end date is after the start date
        end_date = cleaned_data.get("evnt_end")
        if end_date:
            start_date = cleaned_data.get("evnt_start")
            if end_date and start_date and end_date < start_date:
                self.add_error('evnt_end', gettext(
                    "The end date must be after the start date!"
                ))


class EvntcForm(CreatePrams):
    class Meta:
        model = models.EventCode
        exclude = []


class FacicForm(CreatePrams):
    class Meta:
        model = models.FacilityCode
        exclude = []


class FecuForm(CreateTimePrams):
    class Meta:
        model = models.Fecundity
        exclude = []


class FeedForm(CreatePrams):
    class Meta:
        model = models.Feeding
        exclude = []


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


class HeatForm(CreatePrams):
    class Meta:
        model = models.HeathUnit
        exclude = []
        widgets = {
            'inservice_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date"})
        }


class HeatdForm(CreateTimePrams):
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


class IndvtForm(CreatePrams):
    class Meta:
        model = models.IndTreatment
        exclude = []
        widgets = {
            'start_datetime': forms.DateInput(attrs={"placeholder": "Click to select a date...",
                                                     "class": "fp-date-time"}),
            'end_datetime': forms.DateInput(attrs={"placeholder": "Click to select a date...",
                                                   "class": "fp-date-time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # 1) the end date is after the start date and
        end_date = cleaned_data.get("end_datetime")
        if end_date:
            start_date = cleaned_data.get("start_datetime")
            if end_date and start_date and end_date < start_date:
                self.add_error('end_datetime', gettext(
                    "The end date must be after the start date!"
                ))


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


class InstdForm(CreateTimePrams):
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
        widgets = {
            'loc_date': forms.DateInput(attrs={"placeholder": "Click to select a date..", "class": "fp-date-time"}),
        }


class LoccForm(CreatePrams):
    class Meta:
        model = models.LocCode
        exclude = []


class OrgaForm(CreatePrams):
    class Meta:
        model = models.Organization
        exclude = []


class PairForm(CreateTimePrams):
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


class ProgForm(CreateTimePrams):
    class Meta:
        model = models.Program
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['orga_id'].create_url = 'bio_diversity:create_orga'


class ProgaForm(CreatePrams):
    class Meta:
        model = models.ProgAuthority
        exclude = []


class ProtForm(CreateTimePrams):
    class Meta:
        model = models.Protocol
        exclude = []


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


class SpwnForm(CreatePrams):
    class Meta:
        model = models.Spawning
        exclude = []
        widgets = {
            'spwn_date': forms.DateInput(attrs={"placeholder": "Click to select a date...", "class": "fp-date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pair_id'].create_url = 'bio_diversity:create_pair'


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


class TankdForm(CreateTimePrams):
    class Meta:
        model = models.TankDet
        exclude = []


class TeamForm(CreatePrams):
    class Meta:
        model = models.Team
        exclude = []


class TrayForm(CreatePrams):
    class Meta:
        model = models.Tray
        exclude = []


class TraydForm(CreateTimePrams):
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


class TrofdForm(CreateTimePrams):
    class Meta:
        model = models.TroughDet
        exclude = []


class UnitForm(CreatePrams):
    class Meta:
        model = models.UnitCode
        exclude = []
