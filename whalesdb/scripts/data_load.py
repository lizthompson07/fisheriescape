from whalesdb import models


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


def load_sts_status_sts_codes():
    data_array = [
        {
            'sts_id': 1,
            'sts_name': 'Current'
        },
        {
            'sts_id': 2,
            'sts_name': 'Past'
        }
    ]

    for entry in data_array:
        # Do not add entries that are already in the code list
        if not models.StsStatus.objects.filter(sts_name=entry['sts_name']):
            models.StsStatus(entry['sts_id'], entry['sts_name']).save()


load_adcbits()
load_parameter_types()
load_equipment_type_codes()
load_sts_status_sts_codes()