from whalesdb import models

import os


def get_id(model, sort):
    obj = model.objects.all().order_by('-' + sort).values_list()

    n_id = 1
    if obj and obj[0][0]:
        n_id = int(obj[0][0]) + 1

    return n_id


def load_crs(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.CrsCruises

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(crs_name=data[0]):
            #for now, the data file only has the CRS name with no other info
            model(crs_name=data[0]).save()


def load_prj(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.PrjProjects
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(prj_name=data[0]):
            model(prj_name=data[0],
                  prj_descrption=(None if data[1]=='' else data[1]),
                  prj_url=(None if data[2]=='' else data[2])).save()


def load_rtt(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.RttTimezoneCode
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(rtt_abb=data[0]):
            print(str(data))
            rtt_id = get_id(model, "rtt_id")
            model(rtt_id=rtt_id,
                  rtt_abb=data[0],
                  rtt_name=(None if data[1]=='' else data[1]),
                  rtt_offset=(None if data[2]=='' else data[2])).save()


def load_set(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.SetStationEventCode
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(set_name=data[0]):
            print(str(data))
            set_id = get_id(model, "set_id")
            model(set_id=set_id,
                  set_name=data[0],
                  set_description=(None if data[1]=='' else data[1])).save()


def load_stn(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.StnStations
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(stn_name=data[0], stn_revision=data[2]):
            print(str(data))
            # Ignore data[3]
            # We were going to use a stn_status column to indicate 'past' and 'current' stations
            # but since the current station is always the one with the highest revision number
            # we figured it would cut down on potiential errors to exclude the status, which will
            # be easier to add in later.

            model(stn_name=data[0],
                  stn_code=(None if data[1]=='' else data[1]),
                  stn_revision=(None if data[2]=='' else data[2]),
                  stn_planned_lat=(None if data[4]=='' else data[4]),
                  stn_planned_lon=(None if data[5]=='' else data[5]),
                  stn_planned_depth=(None if data[6]=='' else data[6]),
                  stn_notes=(None if data[7]=='' else data[7])).save()


def load_tea(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.TeaTeamMembers
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(tea_last_name=data[1], tea_first_name=data[2]):
            print(str(data))
            model(tea_abb=data[0],
                  tea_last_name=data[1],
                  tea_first_name=data[2]).save()


def load_eqt(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.EqtEquipmentTypeCode
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(eqt_name=data[0]):
            print(str(data))
            eqt_id = get_id(model, "eqt_id")
            model(eqt_id=eqt_id, eqt_name=data[0]).save()


def load_eqa(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.EqaAdcBitsCode
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(eqa_name=data[0]):
            print(str(data))
            eqa_id = get_id(model, "eqa_id")
            model(eqa_id=eqa_id, eqa_name=data[0]).save()


def load_prm(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.PrmParameterCode
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(prm_name=data[0]):
            print(str(data))
            prm_id = get_id(model, "prm_id")
            model(prm_id=prm_id, prm_name=data[0]).save()


def load_emm(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.EmmMakeModel
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        if not model.objects.filter(emm_make=data[0], emm_model=data[1]):
            print(str(data))
            emm_make = data[0]
            emm_model = data[1]
            emm_depth_rating = data[2]
            emm_description = data[3]

            try:
                eqt_type = models.EqtEquipmentTypeCode.objects.get(eqt_name=data[4])
                print(eqt_type)

                model(emm_make=emm_make, emm_model=emm_model, emm_depth_rating=emm_depth_rating,
                      emm_description=emm_description, eqt=eqt_type).save()
            except models.EqtEquipmentTypeCode.DoesNotExist:
                print("Eqt '" + data[4] + "' was not found")


def load_ecp(file_name):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\data\\" + file_name
    model = models.EcpChannelProperties
    print("file: " + file_path)

    file = open(file_path, "r")
    first = True
    for line in file:
        if first:
            first = False
            continue

        data = line.strip().split(',')
        try:
            emm_make = data[0]
            emm_model = data[1]

            emm = models.EmmMakeModel.objects.get(emm_make=data[0], emm_model=data[1])

            if not models.EqrRecorderProperties.objects.filter(emm=emm):
                eqr = models.EqrRecorderProperties(emm=emm, eqc_max_channels=2, eqc_max_sample_rate=-1).save()
            else:
                eqr = models.EqrRecorderProperties.objects.get(emm=emm)

            if not model.objects.filter(emm=eqr):
                print(str(data))

                ecp_channel_no = data[2]
                eqa_adc_bits = data[3]
                ecp_voltage_range = data[4]
                ecp_gain = data[5]

                print("Setting Channel properties for '" + str(emm) + "'")
        except models.EmmMakeModel.DoesNotExist:
            print("Could not find make/model '" + data[0] + "/" + data[1] + "'")


load_crs("CRS-cruises.csv")
load_prj("PRJ-projects.csv")
load_rtt("RTT-timezone types.csv")
load_set("SET-station event types.csv")
load_stn("STN-stations.csv")
load_tea("TEA-team members.csv")

load_eqa("EQA-ADC bits.csv")
load_prm("PRM-parameter types.csv")
load_eqt("EQT-equipment types.csv")
load_emm("EMM-equipment make model.csv")
load_ecp("ECP-channel properties.csv")
