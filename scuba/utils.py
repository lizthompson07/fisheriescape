import math

from django.contrib.auth.models import Group


# open basic access up to anybody who is logged in
def in_scuba_admin_group(user):
    # make sure the following group exist:
    admin_group, created = Group.objects.get_or_create(name="scuba_admin")
    if user:
        return admin_group in user.groups.all()


def in_scuba_crud_group(user):
    # make sure the following group exist:
    crud_group, created = Group.objects.get_or_create(name="scuba_crud")
    if user:
        return in_scuba_admin_group(user) or crud_group in user.groups.all()



def calc_nautical_dist(p0, p1):
    """
    p0 and p1 should be dicts with key 'lat' and 'lng'
    """
    nautical_miles = 3443.8985 * math.acos(
        math.sin(p0["x"] * math.pi / 180) * math.sin(p1["x"] * math.pi / 180) +
        math.cos(p0["x"] * math.pi / 180) * math.cos(p1["x"] * math.pi / 180) *
        math.cos(p1["y"] * math.pi / 180 - p0["y"] * math.pi / 180)
    )
    return nautical_miles