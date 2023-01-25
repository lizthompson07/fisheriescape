from django.utils.translation import gettext_lazy as _

from shared_models.utils import dotdict

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
