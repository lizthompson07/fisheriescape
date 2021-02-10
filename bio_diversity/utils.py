import math

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from bio_diversity import models


def bio_diverisity_authorized(user):
    # return user.is_user and user.groups.filter(name='bio_diversity_user').exists()
    return user.groups.filter(name='bio_diversity_user').exists() or bio_diverisity_admin(user)


def bio_diverisity_admin(user):
    # return user.is_authenticated and user.groups.filter(name='bio_diversity_admin').exists()
    return user.groups.filter(name='bio_diversity_admin').exists()


def get_comment_keywords_dict():
    my_dict = {}
    for obj in models.CommentKeywords.objects.all():
        my_dict[obj.keyword] = obj.adsc_id
    return my_dict


def get_help_text_dict(model=None):
    my_dict = {}
    if not model:
        for obj in models.HelpText.objects.all():
            my_dict[obj.field_name] = str(obj)
    else:
        # If a model is supplied get the fields specific to that model
        for obj in models.HelpText.objects.filter(model=str(model.__name__)):
            my_dict[obj.field_name] = str(obj)

    return my_dict


def get_cont_evnt(contx_tuple):
    contx = contx_tuple[0]
    in_out_dict = {None: "", False: "Origin", True: "Destination"}
    output_list = [contx.evnt_id.evntc_id.__str__(), contx.evnt_id.start_date, in_out_dict[contx_tuple[1]]]
    for cont in [contx.tank_id, contx.cup_id, contx.tray_id, contx.trof_id, contx.draw_id, contx.heat_id]:
        if cont:
            output_list.append("{}".format(cont.__str__()))
            break
    return output_list


def comment_parser(comment_str, anix_indv):
    coke_dict = get_comment_keywords_dict()
    parser_list = coke_dict.keys()
    mortality = False
    for term in parser_list:
        if term.lower() in comment_str.lower():
            adsc = coke_dict[term]
            if adsc.name == "Mortality":
                mortality=True
            indvd_parsed = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                anidc_id=adsc.anidc_id,
                                                adsc_id=adsc,
                                                qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                comments=comment_str,
                                                created_by=anix_indv.created_by,
                                                created_date=anix_indv.created_date,
                                                )
            try:
                indvd_parsed.clean()
                indvd_parsed.save()
            except (ValidationError, IntegrityError):
                pass
    if mortality:
        anix_indv.indv_id.indv_valid = False
        anix_indv.indv_id.save()


def enter_indvd(anix_pk, cleaned_data, det_value, anidc_str, adsc_str):
    row_entered = False
    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False
    if adsc_str:
        indvd = models.IndividualDet(anix_id_id=anix_pk,
                                     anidc_id=models.AnimalDetCode.objects.filter(name=anidc_str).get(),
                                     adsc_id=models.AniDetSubjCode.objects.filter(name=adsc_str).get(),
                                     det_val=det_value,
                                     qual_id=models.QualCode.objects.filter(name="Good").get(),
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
    else:
        indvd = models.IndividualDet(anix_id_id=anix_pk,
                                     anidc_id=models.AnimalDetCode.objects.filter(name=anidc_str).get(),
                                     det_val=det_value,
                                     qual_id=models.QualCode.objects.filter(name="Good").get(),
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
    try:
        indvd.clean()
        indvd.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        pass
    return row_entered


def enter_tank_contx(tank, cleaned_data, final_flag, indv_pk=None, grp_pk=None):
    row_entered = False
    if not tank == "nan":
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     tank_id=models.Tank.objects.filter(name=tank).get(),
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        tank_id=contx.tank_id).get()

        anix = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                    indv_id_id=indv_pk,
                                    grp_id_id=grp_pk,
                                    contx_id_id=contx.pk,
                                    final_contx_flag=final_flag,
                                    created_by=cleaned_data["created_by"],
                                    created_date=cleaned_data["created_date"],
                                    )
        try:
            anix.clean()
            anix.save()
            row_entered = True
        except (ValidationError, IntegrityError):
            pass

    return row_entered
