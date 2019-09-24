from whalesdb import models

import os


def get_id(model, sort):
    obj = model.objects.all().order_by('-' + sort).values_list()

    n_id = 1
    if obj and obj[0][0]:
        n_id = int(obj[0][0]) + 1

    return n_id


def load_adcbits():
    data_array = [
        {
            'eqa_id': 1,
            'eqa_name': '16-bit'
        },
        {
            'eqa_id': 2,
            'eqa_name': '18-bit'
        },
        {
            'eqa_id': 3,
            'eqa_name': '24-bit'
        },

    ]

    for entry in data_array:
        # Do not add entries that are already in the code list
        if not models.EqaAdcBitsCode.objects.filter(eqa_name=entry['eqa_name']):
            models.EqaAdcBitsCode(entry['eqa_id'], entry['eqa_name']).save()


def load_parameter_types():
    data_array = [
        {
            'prm_id': 1,
            'prm_name': 'Temperature'
        },
        {
            'prm_id': 2,
            'prm_name': 'Oxygen'
        },
        {
            'prm_id': 3,
            'prm_name': 'Salinity'
        },
        {
            'prm_id': 4,
            'prm_name': 'Acidity/pH'
        },
        {
            'prm_id': 5,
            'prm_name': 'Pressure'
        },
        {
            'prm_id': 6,
            'prm_name': 'Turbidity'
        },
        {
            'prm_id': 7,
            'prm_name': 'Orientation (roll-pitch-yaw)'
        },
        {
            'prm_id': 8,
            'prm_name': 'Acoustic'
        },
        {
            'prm_id': 9,
            'prm_name': 'OTN tag pings'
        },

    ]

    for entry in data_array:
        # Do not add entries that are already in the code list
        if not models.PrmParameterCode.objects.filter(prm_name=entry['prm_name']):
            models.PrmParameterCode(entry['prm_id'], entry['prm_name']).save()


def load_equipment_type_codes():
    data_array = [
        {
            'eqt_id': 1,
            'eqt_name': 'Acoustic recorder'
        },
        {
            'eqt_id': 2,
            'eqt_name': 'Environmental sensor'
        },
        {
            'eqt_id': 3,
            'eqt_name': 'OTN receiver'
        },

    ]

    for entry in data_array:
        # Do not add entries that are already in the code list
        if not models.EqtEquipmentTypeCode.objects.filter(eqt_name=entry['eqt_name']):
            models.EqtEquipmentTypeCode(entry['eqt_id'], entry['eqt_name']).save()


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
        if not model.objects.filter(tea_last_name=data[0], tea_first_name=data[1]):
            print(str(data))
            model(tea_abb=data[0],
                  tea_last_name=data[1],
                  tea_first_name=data[2]).save()


load_adcbits()
load_parameter_types()
load_equipment_type_codes()

load_crs("CRS-cruises.csv")
load_prj("PRJ-projects.csv")
load_rtt("RTT-timezone types.csv")
load_set("SET-station event types.csv")
load_stn("STN-stations.csv")
load_tea("TEA-team members.csv")