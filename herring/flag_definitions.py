flag_definitions = {
    # length
    1: "fish length is outside of the probable range.",

    # weight
    2: "fish weight is outside of the probable range.",

    # gonad weight
    3: "gonad weight is outside of the probable range.",

    # annulus count
    4: "annulus count is outside of the probable range.",

    # combos
    10: "unexpected fish length to weight ratio.",
    11: "unexpected gonad weight to somatic weight to maturity level combination.",
    12: "unexpected fish length to number of annuli ratio.",
}


def as_choices():
    return [(key, flag_definitions[key]) for key in flag_definitions]

