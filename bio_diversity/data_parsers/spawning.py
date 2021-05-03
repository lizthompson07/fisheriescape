import os
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pandas as pd

from datetime import date, datetime, timedelta


from bio_diversity import models
from bio_diversity import utils


def mactaquac_spawning_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], header=5,  engine='xlrd', sheet_name="RECORDED matings").dropna \
            (how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False
    parsed = True

    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            indv_qs = models.Individual.objects.filter(pit_tag=row["Pit or carlin"])
            indv_qs_male = models.Individual.objects.filter(pit_tag=row["Pit or carlin.1"])
            if len(indv_qs) == 1 and len(indv_qs_male) == 1:
                indv_female = indv_qs.get()
                indv_male = indv_qs_male.get()
            else:
                log_data += "Error parsing row: \n"
                log_data += str(row)
                log_data += "\nFish with PIT {} or PIT {} not found in db\n".format(row["Pit or carlin"], row["Pit or carlin.1"])
                break

            row_date = row["date"].date()
            anix_female = utils.enter_anix(cleaned_data, indv_pk=indv_female.pk)
            anix_male = utils.enter_anix(cleaned_data, indv_pk=indv_male.pk)

            if utils.enter_indvd(anix_female.pk, cleaned_data, row_date, "Female", "Gender", None):
                row_entered = True

            if utils.enter_indvd(anix_female.pk, cleaned_data, row_date, row["Ln"], "Length", None):
                row_entered = True

            if utils.enter_indvd(anix_female.pk, cleaned_data, row_date, 1000 * row["Wt"], "Weight", None):
                row_entered = True

            if utils.enter_indvd(anix_male.pk, cleaned_data, row_date, "Male", "Gender", None):
                row_entered = True

            if utils.enter_indvd(anix_male.pk, cleaned_data, row_date, row["Ln.1"], "Length", None):
                row_entered = True

            if utils.enter_indvd(anix_male.pk, cleaned_data, row_date, 1000 * row["Wt.1"], "Weight", None):
                row_entered = True

            # pair
            prio_dict = {"H": "High", "M": "Normal", "P": "Low"}
            pair = models.Pairing(start_date=row_date,
                                  prio_id=models.PriorityCode.objects.filter(
                                      name__iexact=prio_dict[row["Pri."]]).get(),
                                  pair_prio_id=models.PriorityCode.objects.filter(
                                      name__iexact=prio_dict[row["Pri..2"]]).get(),
                                  cross=row["Tray #"],
                                  valid=True,
                                  indv_id=indv_female,
                                  comments=row["Comment"],
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
            try:
                pair.clean()
                pair.save()
                row_entered = True
            except (ValidationError, IntegrityError):
                pair = models.Pairing.objects.filter(start_date=row_date, indv_id=indv_female).get()

            # sire
            sire = models.Sire(prio_id=models.PriorityCode.objects.filter(name__iexact=prio_dict[row["Pri..1"]]).get(),
                               pair_id=pair,
                               indv_id=indv_male,
                               choice=row["Choice"],
                               comments=row["Comment.1"],
                               created_by=cleaned_data["created_by"],
                               created_date=cleaned_data["created_date"],
                               )
            try:
                sire.clean()
                sire.save()
                row_entered = True
            except (ValidationError, IntegrityError):
                pass

            anix_pair = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                             pair_id=pair,
                                             created_by=cleaned_data["created_by"],
                                             created_date=cleaned_data["created_date"],
                                             )
            try:
                anix_pair.clean()
                anix_pair.save()
                row_entered = True
            except ValidationError:
                pass

            # fecu/dud
            if row["Exp. #"] > 0:
                if utils.enter_spwnd(pair.pk, cleaned_data, int(row["Exp. #"]), "Fecundity", None, "Calculated"):
                    row_entered = True
            else:
                if utils.enter_spwnd(pair.pk, cleaned_data, row["Choice"], "Dud", None, "Good"):
                    row_entered = True

            # grp
            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__isnull=False,
                                                              pair_id=pair,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              indvt_id__isnull=True,
                                                              loc_id__isnull=True,
                                                              )
            if anix_grp_qs.count() == 0:

                grp = models.Group(spec_id=indv_female.spec_id,
                                   stok_id=indv_female.stok_id,
                                   coll_id=models.Collection.objects.filter(name="F1").get(),
                                   grp_year=row_date.year,
                                   grp_valid=False,
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )
                try:
                    grp.clean()
                    grp.save()
                    anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp.pk)
                    anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp.pk, pair_pk=pair.pk)
                    grp.grp_valid = True
                    grp.save()
                except ValidationError:
                    # recovering the group is only doable through the anix with both grp and pair.
                    # no way to find it here, so only make the group valid after anix's created.
                    pass

            elif anix_grp_qs.count() == 1:
                anix_grp = anix_grp_qs.get()
                grp = anix_grp.grp_id

        except Exception as err:
            err_msg = utils.common_err_parser(err)

            parsed = False
            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err_msg)
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False
        if row_entered:
            rows_entered += 1
            rows_parsed += 1
        elif row_parsed:
            rows_parsed += 1

    # evntf
    indv_qs = models.Individual.objects.filter(pit_tag=data["Pit or carlin"][0])
    if len(indv_qs) == 1:
        indv_female = indv_qs.get()
        evntf = models.EventFile(evnt_id_id=cleaned_data["evnt_id"].pk,
                                 stok_id=indv_female.stok_id,
                                 evntfc_id=models.EventFileCode.objects.filter(name="Mating Plan").get(),
                                 evntf_xls=cleaned_data["data_csv"],
                                 created_by=cleaned_data["created_by"],
                                 created_date=cleaned_data["created_date"],
                                 )
        try:
            evntf.clean()
            evntf.save()
        except (ValidationError, IntegrityError) as err:
            # delete mating plan if model did not save
            if type(err) == IntegrityError:
                if os.path.isfile(evntf.evntf_xls.path):
                    os.remove(evntf.evntf_xls.path)

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True


def coldbrook_spawning_parser(cleaned_data):
    log_data = "Loading Data Results: \n"
    rows_parsed = 0
    rows_entered = 0
    try:
        data = pd.read_excel(cleaned_data["data_csv"], header=5, engine='xlrd', sheet_name="Recording").dropna(
            how="all")
        data_dict = data.to_dict('records')
    except Exception as err:
        log_data += "\n File format not valid: {}".format(err.__str__())
        return log_data, False
    parsed = True

    for row in data_dict:
        row_parsed = True
        row_entered = False
        try:
            indv_qs = models.Individual.objects.filter(pit_tag=row["Pit tag"])
            indv_qs_male = models.Individual.objects.filter(pit_tag=row["Pit tag.1"])
            if len(indv_qs) == 1 and len(indv_qs_male) == 1:
                indv_female = indv_qs.get()
                indv_male = indv_qs_male.get()
            else:
                log_data += "Error parsing row: \n"
                log_data += str(row)
                log_data += "\nFish with PIT {} or PIT {} not found in db\n".format(row["Pit tag"], row["Pit tag.1"])
                break

            row_date = datetime.strptime(row["date"], "%Y-%b-%d")
            anix_female = utils.enter_anix(cleaned_data, indv_pk=indv_female.pk)
            anix_male = utils.enter_anix(cleaned_data, indv_pk=indv_male.pk)

            if utils.enter_indvd(anix_female.pk, cleaned_data, row_date, row["Ln"], "Length", None):
                row_entered = True

            if utils.enter_indvd(anix_female.pk, cleaned_data, row_date, row["Wt"], "Weight", None):
                row_entered = True

            if utils.enter_indvd(anix_male.pk, cleaned_data, row_date, row["Ln.1"], "Length", None):
                row_entered = True

            if utils.enter_indvd(anix_male.pk, cleaned_data, row_date, row["Wt.1"], "Weight", None):
                row_entered = True

            # pair
            prio_dict = {"H": "High", "M": "Normal", "P": "Low"}
            pair = models.Pairing(start_date=row_date,
                                  prio_id=models.PriorityCode.objects.filter(
                                      name__iexact=prio_dict[row["Pri."]]).get(),
                                  pair_prio_id=models.PriorityCode.objects.filter(
                                      name__iexact=prio_dict[row["Pri..2"]]).get(),
                                  cross=row["Tray #"],
                                  valid=True,
                                  indv_id=indv_female,
                                  comments=row["Comment"],
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
            try:
                pair.clean()
                pair.save()
                row_entered = True
            except (ValidationError, IntegrityError):
                pair = models.Pairing.objects.filter(start_date=row_date, indv_id=indv_female).get()

            # sire
            sire = models.Sire(prio_id=models.PriorityCode.objects.filter(name__iexact=prio_dict[row["Pri..1"]]).get(),
                               pair_id=pair,
                               indv_id=indv_male,
                               choice=row["Choice"],
                               comments=row["Comment.1"],
                               created_by=cleaned_data["created_by"],
                               created_date=cleaned_data["created_date"],
                               )
            try:
                sire.clean()
                sire.save()
                row_entered = True
            except (ValidationError, IntegrityError):
                pass

            anix_pair = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                             pair_id=pair,
                                             created_by=cleaned_data["created_by"],
                                             created_date=cleaned_data["created_date"],
                                             )
            try:
                anix_pair.clean()
                anix_pair.save()
                row_entered = True
            except ValidationError:
                pass

            # fecu/dud
            if row["Exp. #"] > 0:
                if utils.enter_spwnd(pair.pk, cleaned_data, int(row["Exp. #"]), "Fecundity", None, "Calculated"):
                    row_entered = True
            else:
                if utils.enter_spwnd(pair.pk, cleaned_data, row["Choice"], "Dud", None, "Good"):
                    row_entered = True

            # grp
            anix_grp_qs = models.AniDetailXref.objects.filter(evnt_id=cleaned_data["evnt_id"],
                                                              grp_id__isnull=False,
                                                              pair_id=pair,
                                                              indv_id__isnull=True,
                                                              contx_id__isnull=True,
                                                              indvt_id__isnull=True,
                                                              loc_id__isnull=True,
                                                              )
            if anix_grp_qs.count() == 0:

                grp = models.Group(spec_id=indv_female.spec_id,
                                   stok_id=indv_female.stok_id,
                                   coll_id=models.Collection.objects.filter(name="F1").get(),
                                   grp_year=row_date.year,
                                   grp_valid=False,
                                   created_by=cleaned_data["created_by"],
                                   created_date=cleaned_data["created_date"],
                                   )
                try:
                    grp.clean()
                    grp.save()
                    anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp.pk)
                    anix_grp = utils.enter_anix(cleaned_data, grp_pk=grp.pk, pair_pk=pair.pk)
                    grp.grp_valid = True
                    grp.save()
                except ValidationError:
                    # recovering the group is only doable through the anix with both grp and pair.
                    # no way to find it here, so only make the group valid after anix's created.
                    pass

            elif anix_grp_qs.count() == 1:
                anix_grp = anix_grp_qs.get()
                grp = anix_grp.grp_id

        except Exception as err:
            err_msg = utils.common_err_parser(err)

            parsed = False
            log_data += "Error parsing row: \n"
            log_data += str(row)
            log_data += "\n Error: {}".format(err_msg)
            log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                        "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
            return log_data, False
        if row_entered:
            rows_entered += 1
            rows_parsed += 1
        elif row_parsed:
            rows_parsed += 1

    # evntf
    indv_qs = models.Individual.objects.filter(pit_tag=data["Pit tag"][0])
    if len(indv_qs) == 1:
        indv_female = indv_qs.get()
        evntf = models.EventFile(evnt_id_id=cleaned_data["evnt_id"].pk,
                                 stok_id=indv_female.stok_id,
                                 evntfc_id=models.EventFileCode.objects.filter(name="Mating Plan").get(),
                                 evntf_xls=cleaned_data["data_csv"],
                                 created_by=cleaned_data["created_by"],
                                 created_date=cleaned_data["created_date"],
                                 )
        try:
            evntf.clean()
            evntf.save()
        except (ValidationError, IntegrityError) as err:
            # delete mating plan if model did not save
            if type(err) == IntegrityError:
                if os.path.isfile(evntf.evntf_xls.path):
                    os.remove(evntf.evntf_xls.path)

    log_data += "\n\n\n {} of {} rows parsed \n {} of {} rows entered to " \
                "database".format(rows_parsed, len(data_dict), rows_entered, len(data_dict))
    return log_data, True