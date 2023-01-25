from shared_models.utils import dotdict

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
        "code": None,
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

def get_instances():
    return [get_instance(item.get("id")) for item in object_list]


def get_dict():
    my_dict = dict()
    for item in object_list:
        id = item["id"]
        my_dict[id] = dict()
        for key in item:
            if not key == "id":
                my_dict[id][key] = item[key]
    return my_dict


def get_instance(id):
    instance = get_dict().get(id)
    if instance:
        return dotdict(instance)
    return instance
