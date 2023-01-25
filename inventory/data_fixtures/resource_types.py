from shared_models.utils import dotdict

object_list = [
    {
        "id": 1,
        "label": "dataset",
        "code": "RI_622",
        "notes": "information applies to geographic information"
    },
    {
        "id": 2,
        "label": "non geographic dataset",
        "code": "RI_624",
        "notes": "information applies to non-geographic information"
    },
    {
        "id": 3,
        "label": "derived dataset",
        "code": "n/a",
        "notes": "not an ISO compliant type; internal use only."
    },
    {
        "id": 4,
        "label": "physical collection",
        "code": "n/a",
        "notes": "not an ISO compliant type; internal use only."
    },
    {
        "id": 5,
        "label": "compilation dataset",
        "code": "n/a",
        "notes": "not an ISO compliant type; internal use only."
    },
    {
        "id": 6,
        "label": "series",
        "code": "RI_623",
        "notes": "a collection of datasets complying to the same product specification"
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
