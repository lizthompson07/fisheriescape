import math

from herring.models import FishDetailFlag


def can_read(user):
    if user:
        return bool(hasattr(user, "herring_user"))


def is_admin(user):
    if user:
        return bool(can_read(user) and user.herring_user.is_admin)


def is_crud_user(user):
    # nested under admin
    if user:
        return is_admin(user) or bool(can_read(user) and user.herring_user.is_crud_user)


def get_max_mins(fish):
    species = fish.sample.species
    length = fish.fish_length
    weight = fish.fish_weight
    gonad_weight = fish.gonad_weight
    maturity = fish.maturity_id
    annuli = fish.annulus_count
    a = species.a
    b = species.b

    lookup = {
        10: dict(min=None, max=None),
        11: dict(min=None, max=None),
        12: dict(min=None, max=None),
    }

    # 10: "unexpected fish length to weight ratio."
    if None not in (a, b, length, weight):
        threshold = 0.25
        calc_weight = a * length ** b

        # Only do 25 percent check if calculated weight is outside 5 grams of detail weight.
        det_wgt_min = weight - 5
        det_wgt_max = weight + 5
        if calc_weight < det_wgt_min or calc_weight > det_wgt_max:
            lookup[10]["min"] = calc_weight * (1 - threshold)
            lookup[10]["max"] = calc_weight * (1 + threshold)

    # 11: "unexpected gonad weight to somatic weight to maturity level combination."
    if None not in (weight, gonad_weight, maturity):
        min_max_lookup = {
            1: dict(min=0,
                    max=1),
            2: dict(min=0,
                    max=math.exp(-4.13529659279963 + math.log(weight) * 0.901314871086489)),
            3: dict(min=math.exp(-9.73232467962432 + math.log(weight) * 1.89741087890489),
                    max=math.exp(-7.36823392683834 + math.log(weight) * 1.89014326451594)),
            4: dict(min=math.exp(-3.47650267387848 + math.log(weight) * 1.032305979081),
                    max=math.exp(-1.26270682092335 + math.log(weight) * 1.01753432622181)),
            5: dict(min=math.exp(-5.20139782140475 + math.log(weight) * 1.57823918381865),
                    max=math.exp(-4.17515855708087 + math.log(weight) * 1.56631264086027)),
            6: dict(min=math.exp(-4.98077570284809 + math.log(weight) * 1.53819945023286),
                    max=math.exp(-3.99324471338789 + math.log(weight) * 1.53661353195509)),
            7: dict(min=math.exp(-5.89580204167729 + math.log(weight) * 1.27478993476955),
                    max=math.exp(-2.94435270310896 + math.log(weight) * 1.19636077686861)),
            8: dict(min=math.exp(-7.18685438956137 + math.log(weight) * 1.40456267851141),
                    max=math.exp(-5.52714180205898 + math.log(weight) * 1.39515770753421)),
        }
        if min_max_lookup.get(maturity):
            lookup[11]["min"] = min_max_lookup[maturity]["min"]
            lookup[11]["max"] = min_max_lookup[maturity]["max"]

    # 12: "unexpected fish length to number of annuli ratio."
    if length is not None and annuli is not None:
        lookup[12]["min"] = (-14.3554448587879 + 6.34008000506408E-02 * length)
        lookup[12]["max"] = (-10.1477660949041 + 6.33784283545123E-02 * length)

    return lookup


def make_fish_flags(fish, user):
    # delete all unaccepted flags
    fish.flags.filter(is_accepted=False).delete()
    species = fish.sample.species
    kwargs = {"fish_detail": fish, "created_by": user, }

    length = fish.fish_length
    weight = fish.fish_weight
    gonad_weight = fish.gonad_weight
    maturity = fish.maturity_id
    annuli = fish.annulus_count

    # 1: "fish length is outside of the probable range."
    if length is not None and (length < 5 or length > species.max_length):
        FishDetailFlag.objects.get_or_create(flag_definition=1, **kwargs)
    elif length is not None:
        fish.flags.filter(flag_definition=1).delete()

    # 2: "fish weight is outside of the probable range."
    if weight is not None and (weight < 1 or weight > species.max_weight):
        FishDetailFlag.objects.get_or_create(flag_definition=2, **kwargs)
    elif weight is not None:
        fish.flags.filter(flag_definition=2).delete()

    # 3: "gonad weight is outside of the probable range."
    if gonad_weight is not None and (gonad_weight > species.max_gonad_weight):
        FishDetailFlag.objects.get_or_create(flag_definition=3, **kwargs)
    elif gonad_weight is not None:
        fish.flags.filter(flag_definition=3).delete()

    # 4: "annulus count is outside of the probable range."
    if annuli is not None and (annuli > species.max_annulus_count):
        FishDetailFlag.objects.get_or_create(flag_definition=4, **kwargs)
    elif annuli is not None:
        fish.flags.filter(flag_definition=4).delete()

    min_max_lookup = get_max_mins(fish)

    # 10: "unexpected fish length to weight ratio."
    if None not in (min_max_lookup[10]["min"], min_max_lookup[10]["max"]) and (weight < min_max_lookup[10]["min"] or weight > min_max_lookup[10]["max"]):
        FishDetailFlag.objects.get_or_create(flag_definition=10, **kwargs)
    elif None not in (length, weight):
        fish.flags.filter(flag_definition=10).delete()

    # 11: "unexpected gonad weight to somatic weight to maturity level combination."
    if None not in (min_max_lookup[11]["min"], min_max_lookup[11]["max"]) and (
            gonad_weight < min_max_lookup[11]["min"] or gonad_weight > min_max_lookup[11]["max"]):
        FishDetailFlag.objects.get_or_create(flag_definition=11, **kwargs)
    elif None not in (weight, gonad_weight, maturity):
        fish.flags.filter(flag_definition=11).delete()

    # 12: "unexpected fish length to number of annuli ratio."
    if None not in (min_max_lookup[12]["min"], min_max_lookup[12]["max"]) and (annuli < min_max_lookup[12]["min"] or annuli > min_max_lookup[12]["max"]):
        FishDetailFlag.objects.get_or_create(flag_definition=12, **kwargs)
    elif None not in (length, annuli):
        fish.flags.filter(flag_definition=12).delete()
