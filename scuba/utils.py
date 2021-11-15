import math


def in_scuba_admin_group(user):
    if user:
        return bool(hasattr(user, "scuba_user") and user.scuba_user.is_admin)


def in_scuba_crud_group(user):
    # nested under admin
    if user:
        return in_scuba_admin_group(user) or bool(hasattr(user, "scuba_user") and user.scuba_user.is_crud_user)


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
