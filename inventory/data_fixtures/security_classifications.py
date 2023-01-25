from shared_models.utils import dotdict

object_list = [
    {
        "id": 1,
        "label": "Restricted",
        "code": "RI_485"
    },
    {
        "id": 2,
        "label": "Unclassified",
        "code": "RI_484"
    },
    {
        "id": 6,
        "label": "Confidential",
        "code": "RI_486"
    },
    {
        "id": 7,
        "label": "Secret",
        "code": "RI_487"
    }
]


def get_choices():
    return [(item["id"], f'{item["label"]}') for item in object_list]


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
