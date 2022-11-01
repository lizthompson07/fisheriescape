flag_definitions = {
    # length
    1: "The fish length is outside of the probable range.",

    # weight
    2: "The fish weight is outside of the probable range.",

    # gonad weight
    3: "The gonad weight is outside of the probable range.",

    # annulus count
    4: "The annulus count is outside of the probable range.",

    # combos
    10: "Unexpected fish length to weight ratio.",
    11: "Unexpected gonad weight to somatic weight to maturity level combination.",
    12: "Unexpected fish length to number of annuli ratio.",
}


def as_choices():
    return [(key, flag_definitions[key]) for key in flag_definitions]

