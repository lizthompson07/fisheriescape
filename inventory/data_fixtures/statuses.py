object_list = [
    {
        "id": 1,
        "label": "completed",
        "code": "RI_593",
        "notes": "production of the data has been completed"
    },
    {
        "id": 2,
        "label": "obsolete",
        "code": "RI_595",
        "notes": "data is no longer relevant"
    },
    {
        "id": 3,
        "label": "ongoing",
        "code": "RI_596",
        "notes": "data is continually being updated"
    },
    {
        "id": 4,
        "label": "historical archive",
        "code": "RI_594",
        "notes": "data has been stored in an offline storage facility"
    },
    {
        "id": 5,
        "label": "M.I.A.",
        "code": null,
        "notes": "data is missing in action (not ISO compliant)"
    },
    {
        "id": 9,
        "label": "under development",
        "code": "RI_599",
        "notes": "data is currently in the progress of being created"
    },
    {
        "id": 10,
        "label": "planned",
        "code": "RI_597",
        "notes": "fixed date has been established upon or by which the data will be created or updated"
    },
    {
        "id": 12,
        "label": "required",
        "code": "RI_598",
        "notes": "data needs to be generated or updated"
    }
]


def get_choices():
    return [(item["id"], f'{item["label"]}') for item in object_list]


def get_dict():
    my_dict = dict()
    for item in object_list:
        my_dict[item["id"]] = dict()
        my_dict[item["id"]]["label"] = item["label"]
        my_dict[item["id"]]["code"] = item["code"]
        my_dict[item["id"]]["notes"] = item["notes"]
    return my_dict
