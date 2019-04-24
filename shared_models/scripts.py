from .import models

def pad_codes():
    for port in models.Port.objects.all():
        if len(port.district_code) == 1:
            port.district_code = "0{}".format(port.district_code)
            port.save()
        if len(port.port_code) == 1:
            port.port_code = "0{}".format(port.port_code)
            port.save()