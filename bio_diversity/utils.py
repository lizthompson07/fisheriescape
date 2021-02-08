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


def get_cont_evnt(contx):
    output_list = [contx.evnt_id.evntc_id.__str__(), contx.evnt_id.evnt_start]
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
