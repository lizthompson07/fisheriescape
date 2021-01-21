from bio_diversity import models


def bio_diverisity_authorized(user):
    # return user.is_authenticated and user.groups.filter(name='bio_diversity_admin').exists()
    return user.groups.filter(name='bio_diversity_admin').exists()


def get_help_text_dict():
    my_dict = {}
    for obj in models.HelpText.objects.all():
        my_dict[obj.field_name] = str(obj)

    return my_dict
