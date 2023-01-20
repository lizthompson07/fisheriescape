object_list = [
    {
        "id": 1,
        "label": "EPSG:4269 LL (Nad83)",
        "code": "EPSG:4269",
        "codespace": "http://www.epsg-registry.org"
    },
    {
        "id": 2,
        "label": "EPSG:3978 Lambert Conic Conformal (Nad83)",
        "code": "EPSG:3978",
        "codespace": "http://www.epsg-registry.org"
    },
    {
        "id": 3,
        "label": "EPSG:3979 Lambert Conic Conformal (CSRS)",
        "code": "EPSG:3979",
        "codespace": "http://www.epsg-registry.org"
    },
    {
        "id": 4,
        "label": "EPSG:4326 WGS84",
        "code": "EPSG:4326",
        "codespace": "http://www.epsg-registry.org"
    },
    {
        "id": 5,
        "label": "EPSG 3857",
        "code": "EPSG 3857",
        "codespace": "http://www.epsg-registry.org"
    },
    {
        "id": 6,
        "label": "EPSG 4617",
        "code": "EPSG 4617",
        "codespace": "http://www.epsg-registry.org"
    },
    {
        "id": 7,
        "label": "EPSG 32198",
        "code": "EPSG 32198",
        "codespace": "http://www.epsg-registry.org"
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
        my_dict[item["id"]]["codespace"] = item["codespace"]
    return my_dict
