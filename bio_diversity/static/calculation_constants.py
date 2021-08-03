
# sample usage:  daily_dev = 100 / math.exp(DEVELOPMENT_ALPHA * math.exp(DEVELOPMENT_BETA * degree_day))
DEVELOPMENT_ALPHA = 6.002994
DEVELOPMENT_BETA = -0.03070758

sex_dict = {"M": "Male",
            "Male": "Male",
            "Female": "Female",
            "Immature": "Immature",
            "F": "Female",
            "IT": "Immature",
            "I": "Immature"}

# Pairing priority options
prio_dict = {"H": "High",
             "M": "Medium",
             "L": "Low",
             "P": "Pairwise",
             "E": "Extra Male"}

sfa_nums = [15, 16, 17, 18, 19, 20, 21, 22, 23]

collection_evntc_list = ["electrofishing", "bypass collection", "smolt wheel collection", "smolt collection",
                         "fall parr collection"]

egg_dev_evntc_list = ["egg development", "heath unit transfer", "picking", "shocking"]