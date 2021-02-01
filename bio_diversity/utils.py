from django.core.exceptions import ValidationError
from django.db import IntegrityError

from bio_diversity import models


def bio_diverisity_authorized(user):
    # return user.is_user and user.groups.filter(name='bio_diversity_user').exists()
    return user.groups.filter(name='bio_diversity_user').exists() or bio_diverisity_admin(user)


def bio_diverisity_admin(user):
    # return user.is_authenticated and user.groups.filter(name='bio_diversity_admin').exists()
    return user.groups.filter(name='bio_diversity_admin').exists()


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


def get_cont_evnt(contx):
    output_list = [contx.evnt_id.evntc_id.__str__(), contx.evnt_id.evnt_start]
    for cont in [contx.tank_id, contx.cup_id, contx.tray_id, contx.trof_id, contx.draw_id, contx.heat_id]:
        if cont:
            output_list.append("{}".format(cont.__str__()))
            break
    return output_list


def comment_parser(comment_str, anix_indv):
    parser_list = ["bad shape"]
    for term in parser_list:
        if term in comment_str.lower():
            adsc = models.AniDetSubjCode.objects.filter(name__icontains=term).get()
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

