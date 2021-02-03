import inspect
import math
from datetime import date, datetime, time

from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import modelformset_factory
from django.utils.timezone import make_aware
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
        self.fields['start_time'] = forms.CharField(required=False, max_length=4, min_length=4)
        self.fields['end_time'] = forms.CharField(required=False, max_length=4, min_length=4)

    def clean(self):
        cleaned_data = super().clean()
        # we have to make sure
        # the end datetime is after the start datetime
        # and set the datetime values
        if cleaned_data["start_time"]:
            start_time = make_aware(datetime.strptime(cleaned_data["start_time"], '%H%M').time())
        else:
            start_time = make_aware(time(0, 0))
        cleaned_data["start_datetime"] = datetime.combine(cleaned_data["start_date"], start_time)
        if cleaned_data["end_date"]:
            if cleaned_data["end_time"]:
                end_time = make_aware(datetime.strptime(cleaned_data["end_time"], '%H%M').time())
            else:
                end_time = make_aware(time(0, 0))
            cleaned_data["end_datetime"] = datetime.combine(cleaned_data["end_date"], end_time)

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


class CupForm(CreatePrams):
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
                row_entered = False
                try:
                    loc = models.Location(evnt_id_id=cleaned_data["evnt_id"].pk,
                                          locc_id_id=1,
                                          rive_id=models.RiverCode.objects.filter(name=row["River"]).get(),
                                          subr_id=models.SubRiverCode.objects.filter(name__iexact=row["Branch"]).get(),
                                          relc_id=models.ReleaseSiteCode.objects.filter(name__iexact=row["Site"]).get(),
                                          start_datetime=datetime.strptime(row["Date"], "%Y-%b-%d"),
                                          comments=row["Comments"],
                                          created_by=cleaned_data["created_by"],
                                          created_date=cleaned_data["created_date"],
                                          )
                    try:
                        loc.clean()
                        loc.save()
                        row_entered = True
                    except ValidationError:
                        loc = models.Location.objects.filter(evnt_id=loc.evnt_id, locc_id=loc.locc_id,
                                                             rive_id=loc.rive_id, subr_id=loc.subr_id,
                                                             relc_id=loc.relc_id, start_datetime=loc.start_datetime).get()

                    if not math.isnan(row["temp"]):
                        env = models.EnvCondition(loc_id_id=loc.pk,
                                                  inst_id=models.Instrument.objects.first(),
                                                  envc_id=models.EnvCode.objects.filter(name__iexact="Temperature").get(),
                                                  env_val=row["temp"],
                                                  start_datetime=datetime.strptime(row["Date"], "%Y-%b-%d"),
                                                  env_avg=False,
                                                  qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                  created_by=cleaned_data["created_by"],
                                                  created_date=cleaned_data["created_date"],
                                                  )
                        try:
                            env.clean()
                            env.save()
                            row_entered = True
                        except ValidationError:
                            pass
                    cnt = False
                    if not math.isnan(row["# of salmon collected"]):
                        cnt = models.Count(loc_id_id=loc.pk,
                                           spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                           cntc_id=models.CountCode.objects.filter(name__iexact="Fish Caught").get(),
                                           cnt=row["# of salmon collected"],
                                           est=False,
                                           created_by=cleaned_data["created_by"],
                                           created_date=cleaned_data["created_date"],
                                           )
                        try:
                            cnt.clean()
                            cnt.save()
                            row_entered = True
                        except ValidationError:
                            cnt = models.Count.objects.filter(loc_id=cnt.loc_id, cntc_id=cnt.cntc_id, cnt=cnt.cnt).get()

                    elif not math.isnan(row["# of salmon observed"]):
                            cnt = models.Count(loc_id_id=loc.pk,
                                               spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                                               cntc_id=models.CountCode.objects.filter(
                                                   name__iexact="Fish Observed").get(),
                                               cnt=row["# of salmon observed"],
                                               est=False,
                                               created_by=cleaned_data["created_by"],
                                               created_date=cleaned_data["created_date"],
                                               )
                            try:
                                cnt.clean()
                                cnt.save()
                                row_entered = True
                            except ValidationError:
                                cnt = models.Count.objects.filter(loc_id=cnt.loc_id, cntc_id=cnt.cntc_id,
                                                                  cnt=cnt.cnt).get()
                    if cnt:
                        if not math.isnan(row["fishing seconds"]):
                            cntd = models.CountDet(cnt_id=cnt,
                                                   anidc_id=models.AnimalDetCode.objects.filter(name__iexact="Electrofishing Seconds").get(),
                                                   det_val=row["fishing seconds"],
                                                   qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                   created_by=cleaned_data["created_by"],
                                                   created_date=cleaned_data["created_date"],
                                                   )
                            try:
                                cntd.clean()
                                cntd.save()
                                row_entered = True
                            except ValidationError:
                                pass

                        if not math.isnan(row["Voltage"]):
                            cntd = models.CountDet(cnt_id=cnt,
                                                   anidc_id=models.AnimalDetCode.objects.filter(name__iexact="Voltage").get(),
                                                   det_val=row["Voltage"],
                                                   qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                   created_by=cleaned_data["created_by"],
                                                   created_date=cleaned_data["created_date"],
                                                   )
                            try:
                                cntd.clean()
                                cntd.save()
                                row_entered = True
                            except ValidationError:
                                pass

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
                                           det_val=data["# of salmon collected"].sum(),
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
                        row_entered = True
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
                            row_entered = True
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
                            row_entered = True
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
                        row_entered = True
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
                        pass

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
                            pass
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
                            pass
                    if not math.isnan(row["Vial"]):
                        indvd_length = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                            anidc_id=models.AnimalDetCode.objects.filter(
                                                                name="Vial").get(),
                                                            det_val=row["Vial"],
                                                            qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                            created_by=cleaned_data["created_by"],
                                                            created_date=cleaned_data["created_date"],
                                                            )
                        try:
                            indvd_length.clean()
                            indvd_length.save()
                            row_entered = True
                        except ValidationError:
                            pass
                    if not math.isnan(row["Box"]):
                        indvd_length = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                            anidc_id=models.AnimalDetCode.objects.filter(
                                                                name="Box").get(),
                                                            det_val=row["Box"],
                                                            qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                            created_by=cleaned_data["created_by"],
                                                            created_date=cleaned_data["created_date"],
                                                            )
                        try:
                            indvd_length.clean()
                            indvd_length.save()
                            row_entered = True
                        except ValidationError:
                            pass
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

            # ---------------------------TAGGING MACTAQUAC DATA ENTRY----------------------------------------
        elif cleaned_data["evntc_id"].__str__() == "Tagging" and cleaned_data["facic_id"].__str__() == "Mactaquac":
            try:
                data = pd.read_excel(cleaned_data["data_csv"], engine='openpyxl', header=0,
                                     converters={'to tank': str})
                data["Comments"] = data["Comments"].fillna('')
                data_dict = data.to_dict('records')
            except Exception as err:
                raise Exception("File format not valid: {}".format(err.__str__()))
            parsed = True
            self.request.session["load_success"] = True
            try:
                grp_id = models.Group.objects.filter(stok_id__name__iexact=data_dict[0]["Stock"],
                                                     coll_id__name__iexact=data_dict[0]["Collection"]).get().pk
                anix_grp = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                grp_id_id=grp_id,
                                                created_by=cleaned_data["created_by"],
                                                created_date=cleaned_data["created_date"],
                                                )
                try:
                    anix_grp.clean()
                    anix_grp.save()
                    row_entered = True
                except ValidationError:
                    pass
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
                                             coll_id=models.Collection.objects.filter(name=row["Collection"]).get(),
                                             pit_tag=row["PIT"],
                                             indv_valid=True,
                                             comments=row["Comments"],
                                             created_by=cleaned_data["created_by"],
                                             created_date=cleaned_data["created_date"],
                                             )
                    try:
                        indv.clean()
                        indv.save()
                        row_entered = True
                    except (ValidationError, IntegrityError):
                        indv = models.Individual.objects.filter(ufid=indv.ufid, pit_tag=indv.pit_tag).get()

                    if not row["Destination Pond"] == "nan":
                        contx_to = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                        tank_id=models.Tank.objects.filter(name=row["Destination Pond"]).get(),
                                                        created_by=cleaned_data["created_by"],
                                                        created_date=cleaned_data["created_date"],
                                                        )
                        try:
                            contx_to.clean()
                            contx_to.save()
                            row_entered = True
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
                            row_entered = True
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
                        row_entered = True
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
                        pass

                    if not math.isnan(row["Length (cm)"]):
                        indvd_length = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                            anidc_id=models.AnimalDetCode.objects.filter(
                                                                name="Length").get(),
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
                            pass
                    if not math.isnan(row["Weight (g)"]):
                        indvd_mass = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                          anidc_id=models.AnimalDetCode.objects.filter(
                                                              name="Weight").get(),
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
                            pass
                    if not math.isnan(row["Vial Number"]):
                        indvd_length = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                            anidc_id=models.AnimalDetCode.objects.filter(
                                                                name="Vial").get(),
                                                            det_val=row["Vial Number"],
                                                            qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                            created_by=cleaned_data["created_by"],
                                                            created_date=cleaned_data["created_date"],
                                                            )
                        try:
                            indvd_length.clean()
                            indvd_length.save()
                            row_entered = True
                        except ValidationError:
                            pass
                    if row["Comments"]:
                        comment_parser(row["Comments"], anix_indv)
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
                        log_data += "Error parsing row: \n"
                        log_data += str(row)
                        log_data += "\nFish with PIT {} not found in db\n".format(row["PIT"])

                    if indv:
                        anix_indv = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                                         indv_id_id=indv.pk,
                                                         created_by=cleaned_data["created_by"],
                                                         created_date=cleaned_data["created_date"],
                                                         )
                        try:
                            anix_indv.clean()
                            anix_indv.save()
                            row_entered = True
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
                                row_entered = True
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
                                row_entered = True
                            except ValidationError:
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
                                pass
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


class EnvForm(CreateTimePrams):
    class Meta:
        model = models.EnvCondition
        exclude = []
        widgets = {
        }


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


class EvntForm(CreateTimePrams):
    class Meta:
        model = models.Event
        exclude = []
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team_id'].create_url = 'bio_diversity:create_team'


class EvntcForm(CreatePrams):
    class Meta:
        model = models.EventCode
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
        self.fields['start_datetime'].widget = forms.HiddenInput()
        self.fields['start_datetime'].required = False
        self.fields['start_date'] = forms.DateField(widget=forms.DateInput(
            attrs={"placeholder": "Click to select a date...", "class": "fp-date"}))
        self.fields['start_time'] = forms.CharField(required=False, max_length=4, min_length=4)

    def save(self, commit=True):
        obj = super().save(commit=False)  # here the object is not commited in db
        if self.cleaned_data["start_time"]:
            start_time = datetime.strptime(self.cleaned_data["start_time"], '%H%M').time()
        else:
            start_time = time(0, 0)
        obj.start_datetime = datetime.combine(self.cleaned_data["start_date"], start_time)
        obj.save()
        return obj


class LoccForm(CreatePrams):
    class Meta:
        model = models.LocCode
        exclude = []


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['orga_id'].create_url = 'bio_diversity:create_orga'


class ProgaForm(CreatePrams):
    class Meta:
        model = models.ProgAuthority
        exclude = []


class ProtForm(CreateDatePrams):
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


class TankdForm(CreateDatePrams):
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
