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
        my_dict[item["id"]] = dict()
        my_dict[item["id"]]["label"] = item["label"]
        my_dict[item["id"]]["code"] = item["code"]
    return my_dict
