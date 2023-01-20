object_list = [
    {
        "id": 2,
        "frequency": "Daily",
        "code": "RI_533",
        "notes": "data is updated each day"
    },
    {
        "id": 3,
        "frequency": "Weekly",
        "code": "RI_534",
        "notes": ""
    },
    {
        "id": 4,
        "frequency": "Monthly",
        "code": "RI_536",
        "notes": ""
    },
    {
        "id": 5,
        "frequency": "Quartely",
        "code": "RI_537",
        "notes": ""
    },
    {
        "id": 6,
        "frequency": "Annually",
        "code": "RI_539",
        "notes": "data is updated every year"
    },
    {
        "id": 7,
        "frequency": "Biannual",
        "code": "RI_538",
        "notes": ""
    },
    {
        "id": 8,
        "frequency": "Irregular",
        "code": "RI_541",
        "notes": ""
    },
    {
        "id": 9,
        "frequency": "Continual",
        "code": "RI_532",
        "notes": "data is repeatedly and frequently updated"
    },
    {
        "id": 10,
        "frequency": "As needed",
        "code": "RI_540",
        "notes": ""
    },
    {
        "id": 11,
        "frequency": "Not planned",
        "code": "RI_542",
        "notes": ""
    },
    {
        "id": 12,
        "frequency": "Unknown",
        "code": "RI_543",
        "notes": "frequency of maintenance for the data is not known"
    }
]


def get_choices():
    return [(item["id"], f'{item["frequency"]}') for item in object_list]


def get_dict():
    my_dict = dict()
    for item in object_list:
        my_dict[item["id"]] = dict()
        my_dict[item["id"]]["frequency"] = item["frequency"]
        my_dict[item["id"]]["code"] = item["code"]
        my_dict[item["id"]]["notes"] = item["notes"]
    return my_dict
