from django.utils.translation import gettext_lazy as _

object_list = [
    {
        "id": 1,
        "label": "utf8",
        "code": "RI_458",
        "notes": _("8-bit variable size UCS Transfer Format, based on ISO IEC 10646")
    },
    {
        "id": 2,
        "label": "usAscii",
        "code": "RI_478",
        "notes": _("united states ASCII code set (ISO 646 US)")
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
