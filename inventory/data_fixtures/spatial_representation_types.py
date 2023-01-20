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
        my_dict[item["id"]] = dict()
        my_dict[item["id"]]["label"] = item["label"]
        my_dict[item["id"]]["code"] = item["code"]
        my_dict[item["id"]]["notes"] = item["notes"]
    return my_dict
