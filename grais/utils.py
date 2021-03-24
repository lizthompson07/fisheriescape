from django.contrib.auth.models import Group

def in_grais_admin_group(user):
    # make sure the following group exist:
    group, created = Group.objects.get_or_create(name="grais_admin")
    if user:
        return group in user.groups.all()

def in_grais_group(user):
    # make sure the following group exist:
    read_group, created = Group.objects.get_or_create(name="grais_access")
    if user:
        return read_group in user.groups.all()