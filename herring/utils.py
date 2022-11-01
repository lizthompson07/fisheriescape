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


def make_fish_flags(fish, user):
    # delete all unaccepted flags
    fish.flags.filter(is_accepted=False).delete()
    kwargs = {"fish_detail": fish, "created_by": user, }

    length = fish.fish_length
    weight = fish.fish_weight
    gweight = fish.gonad_weight
    annuli = fish.annulus_count
    # 2: "fish length is outside of the probable range."
    if length and (length < 5 or length > 400):
        FishDetailFlag.objects.create(flag_definition=1, **kwargs)
    # 4: "fish weight is outside of the probable range."
    if weight and (weight < 1 or weight > 412):
        FishDetailFlag.objects.create(flag_definition=2, **kwargs)
    # 6: "gonad weight is outside of the probable range."
    if gweight and (gweight < 0 or gweight > 89):
        FishDetailFlag.objects.create(flag_definition=3, **kwargs)
    # 8: "annulus count is outside of the probable range."
    if annuli and (annuli < 0 or annuli > 10):
        FishDetailFlag.objects.create(flag_definition=4, **kwargs)


    # 10: "unexpected fish length to weight ratio."

    if length and weight:
        min_weight = math.e**(-12.978 + 3.18 * math.log(length))
        max_weight = math.e**(-12.505 + 3.18 * math.log(length))
        if weight < min_weight or weight > max_weight:
            FishDetailFlag.objects.create(flag_definition=10, **kwargs)
        print(min_weight, max_weight)

    # 11: "unexpected gonad weight to somatic weight to maturity level combination."
    # 12: "unexpected fish length to number of annuli ratio."




    """if (testId === 204) {
        var independentVar = $("#id_fish_length")[0].value
        var dependentVar = $("#id_fish_weight")[0].value
        if (independentVar !== "" && dependentVar !== "") {
            // set the strings to numbers for further processing
            independentVar = Number($("#id_fish_length")[0].value)
            dependentVar = Number($("#id_fish_weight")[0].value)
            var independentName = "fish length"
            var dependentName = "fish weight"
            var min = Math.exp(-12.978 + 3.18 * Math.log(independentVar))
            var max = Math.exp(-12.505 + 3.18 * Math.log(independentVar))
            var msgLite = `Improbable measurement for ${independentName} : ${dependentName} ratio`
            var msg = `The ${independentName} : ${dependentName} ratio is outside of the probable range. \n\nFor the given value of ${independentName}, ${dependentName} most commonly ranges between ${parseFloat(Math.round(min * 100) / 100).toFixed(1)} and ${parseFloat(Math.round(max * 100) / 100).toFixed(1)}. \n\nAre you confident in your measurements? \n\nPress [y] for YES or [n] for NO.`

        }
        else {
            stop = true
        }
    }
    else if (testId === 207) {
        var independentVar = $("#id_fish_weight")[0].value
        var dependentVar = $("#id_gonad_weight")[0].value
        var factor = Number($("#id_maturity")[0].value)
        // only do the test if all vars are present

        if (independentVar !== "" && dependentVar !== "" && factor !== "") {
            // set the strings to numbers for further processing
            independentVar = Number($("#id_fish_weight")[0].value)
            dependentVar = Number($("#id_gonad_weight")[0].value)

            var independentName = "somatic weight"
            var dependentName = "gonad weight"
            if (factor === 1) {
                min = 0
                max = 1
            }
            else if (factor === 2) {
                min = 0
                max = Math.exp(-4.13529659279963 + Math.log(independentVar) * 0.901314871086489)
            }
            else if (factor === 3) {
                min = Math.exp(-9.73232467962432 + Math.log(independentVar) * 1.89741087890489)
                max = Math.exp(-7.36823392683834 + Math.log(independentVar) * 1.89014326451594)
            }
            else if (factor === 4) {
                min = Math.exp(-3.47650267387848 + Math.log(independentVar) * 1.032305979081)
                max = Math.exp(-1.26270682092335 + Math.log(independentVar) * 1.01753432622181)
            }
            else if (factor === 5) {
                min = Math.exp(-5.20139782140475 + Math.log(independentVar) * 1.57823918381865)
                max = Math.exp(-4.17515855708087 + Math.log(independentVar) * 1.56631264086027)
            }
            else if (factor === 6) {
                min = Math.exp(-4.98077570284809 + Math.log(independentVar) * 1.53819945023286)
                max = Math.exp(-3.99324471338789 + Math.log(independentVar) * 1.53661353195509)
            }
            else if (factor === 7) {
                min = Math.exp(-5.89580204167729 + Math.log(independentVar) * 1.27478993476955)
                max = Math.exp(-2.94435270310896 + Math.log(independentVar) * 1.19636077686861)
            }
            else if (factor === 8) {
                min = Math.exp(-7.18685438956137 + Math.log(independentVar) * 1.40456267851141)
                max = Math.exp(-5.52714180205898 + Math.log(independentVar) * 1.39515770753421)
            }

            var msgLite = `Improbable measurement for ${independentName} : ${dependentName} ratio`
            var msg = `The ${independentName} : ${dependentName} ratio is outside of the probable range. \n\nFor the given value of ${independentName} at maturity level ${factor}, ${dependentName} most commonly ranges between ${parseFloat(Math.round(min * 100) / 100).toFixed(1)} and ${parseFloat(Math.round(max * 100) / 100).toFixed(1)}. \n\nAre you confident in your measurements? \n\nPress [y] for YES or [n] for NO.`
        }
        else {
            stop = true
        }
    }
    else if (testId === 209) {
        var independentVar = $("#id_fish_length")[0].value
        var dependentVar = $("#id_annulus_count")[0].value
        if (independentVar !== "" && dependentVar !== "") {
            // set the strings to numbers for further processing
            var independentVar = Number($("#id_fish_length")[0].value)
            var dependentVar = Number($("#id_annulus_count")[0].value)
            var independentName = "fish length"
            var dependentName = "annulus count"
            var min = (-14.3554448587879 + 6.34008000506408E-02 * independentVar)
            var max = (-10.1477660949041 + 6.33784283545123E-02 * independentVar)

            var msgLite = `Improbable measurement for ${independentName} : ${dependentName} ratio`
            var msg = `The ${independentName} : ${dependentName} ratio is outside of the probable range. \n\nFor the given value of ${independentName}, ${dependentName} most commonly ranges between ${parseFloat(Math.round(min * 100) / 100).toFixed(1)} and ${parseFloat(Math.round(max * 100) / 100).toFixed(1)}. \n\nAre you confident in your measurements? \n\nPress [y] for YES or [n] for NO.`
        }
        else {
            stop = true
        }
        """