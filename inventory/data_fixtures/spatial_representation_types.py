from shared_models.utils import dotdict

object_list = [
    {
        "id": 5,
        "label": "vector",
        "code": "RI_635",
        "notes": "vector data is used to represent geographic data"
    },
    {
        "id": 6,
        "label": "grid",
        "code": "RI_636",
        "notes": "grid data is used to represent geographic data"
    },
    {
        "id": 7,
        "label": "textTable",
        "code": "RI_637",
        "notes": "textual or tabular data is used to represent geographic data"
    },
    {
        "id": 8,
        "label": "tin",
        "code": "RI_638",
        "notes": "triangulated irregular network"
    },
    {
        "id": 9,
        "label": "video",
        "code": "RI_640",
        "notes": "scene from a video recording"
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
