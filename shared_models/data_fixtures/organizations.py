from shared_models.utils import dotdict

object_list = [
    {
        "id": 1,
        "name_eng": "Aquatic Resources Division",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 2,
        "name_eng": "Canadian Rivers Institute",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 3,
        "name_eng": "Carver consultant",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 4,
        "name_eng": "Charlo Salmonid Enhancement Center Inc.",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 5,
        "name_eng": "Maritimes Biotechnology Coordination Office (DFO)",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 6,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "343 Université Ave",
        "city": "Moncton",
        "postal_code": "E1C 5K4",
        "location_id": 7
    },
    {
        "id": 7,
        "name_eng": "Institut national de la recherche scientifique ETE",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 8,
        "name_eng": "Integrated Science Data Management (DFO)",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 9,
        "name_eng": "Kouchibouguac National Park",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 10,
        "name_eng": "La Maison Beausoleil Inc.",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 11,
        "name_eng": "Mallet Research Étang Ruisseau Bar Ltd.",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 12,
        "name_eng": "Miramichi Salmon Association",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 13,
        "name_eng": "Mount Allison University",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 14,
        "name_eng": "Université de Moncton",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 15,
        "name_eng": "University of New brunswick",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 16,
        "name_eng": "University of Windsor",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 17,
        "name_eng": "Dalhousie University",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 18,
        "name_eng": "Atlantic Veterinary College; UPEI",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 19,
        "name_eng": "INRS University",
        "name_fre": "Institut national de la recherche scientifique",
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 20,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "867 Lakeshore Rd",
        "city": "Burlington",
        "postal_code": "L7S 1A1",
        "location_id": 12
    },
    {
        "id": 21,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "520 Exmouth St",
        "city": "Sarnia",
        "postal_code": "N7T 8B1",
        "location_id": 12
    },
    {
        "id": 22,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "501 University Cres",
        "city": "Winnipeg",
        "postal_code": "R3T 2N6",
        "location_id": 6
    },
    {
        "id": 23,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "P.O. Box: 1006",
        "city": "Dartmouth",
        "postal_code": "B2Y 4A2",
        "location_id": 10
    },
    {
        "id": 24,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "125 Marine Science Drive",
        "city": "St. Andrews",
        "postal_code": "E5B OE4",
        "location_id": 7
    },
    {
        "id": 25,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "1219 Queen St E",
        "city": "Sault Ste. Marie",
        "postal_code": "P6A 2E5",
        "location_id": 12
    },
    {
        "id": 26,
        "name_eng": "University of Toronto",
        "name_fre": "University of Toronto",
        "abbrev": "U of T",
        "address": "27 King's College Cir",
        "city": "Toronto",
        "postal_code": None,
        "location_id": 12
    },
    {
        "id": 27,
        "name_eng": "University of Alberta",
        "name_fre": "University of Alberta",
        "abbrev": None,
        "address": "116 St & 85 Ave,",
        "city": "Edmonton",
        "postal_code": "T6G 2R3",
        "location_id": 1
    },
    {
        "id": 28,
        "name_eng": "Great Lakes Laboratory for Fisheries and Aquatic Sciences",
        "name_fre": None,
        "abbrev": None,
        "address": "867 Lakeshore Road",
        "city": "Burlington",
        "postal_code": "L7R 4A6",
        "location_id": None
    },
    {
        "id": 29,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "PO Box 6000, 9860 West Saanich Road",
        "city": "Sidney",
        "postal_code": "V8L 4B2",
        "location_id": None
    },
    {
        "id": 30,
        "name_eng": "Natural Resources Canada",
        "name_fre": None,
        "abbrev": None,
        "address": "1 Challenger Drive, P.O. Box 1006 , 4th Floor , Room. M-412A\n                        ",
        "city": "Dartmouth",
        "postal_code": "B2Y 4A2",
        "location_id": None
    },
    {
        "id": 31,
        "name_eng": "Canadian Museum of Nature",
        "name_fre": None,
        "abbrev": None,
        "address": "240 McLeod Street",
        "city": "Ottawa",
        "postal_code": "K2P 2R1",
        "location_id": None
    },
    {
        "id": 32,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "#301 5204- 50 Avenue",
        "city": "Yellowknife",
        "postal_code": "X1A 1E2",
        "location_id": None
    },
    {
        "id": 33,
        "name_eng": "Stantec",
        "name_fre": None,
        "abbrev": None,
        "address": "501 University Crescent",
        "city": "Winnipeg",
        "postal_code": "R3T 2N6",
        "location_id": None
    },
    {
        "id": 34,
        "name_eng": "University of Manitoba",
        "name_fre": None,
        "abbrev": None,
        "address": "495 Wallace Building",
        "city": "Winnipeg",
        "postal_code": "R3T 2N2",
        "location_id": None
    },
    {
        "id": 35,
        "name_eng": "Fisheries and Marine Institute of Memorial University",
        "name_fre": None,
        "abbrev": None,
        "address": "P.O. Box 4920, St. John's, NL Canada",
        "city": "St. John's",
        "postal_code": "A1C 5R3",
        "location_id": None
    },
    {
        "id": 36,
        "name_eng": "Department of Biological Sciences University of Alberta",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 37,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "4th Floor - 630 Queen Elizabeth P.O. Box 358",
        "city": "Iqaluit",
        "postal_code": "X0A 0H0",
        "location_id": None
    },
    {
        "id": 38,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "42043 MacKenzie Highway",
        "city": "Hay River",
        "postal_code": "X0E 0R9",
        "location_id": None
    },
    {
        "id": 39,
        "name_eng": "Center for Earth Observation Science",
        "name_fre": None,
        "abbrev": None,
        "address": "482 Wallace Building University of Manitoba",
        "city": "Winnipeg",
        "postal_code": "R3T 2N2",
        "location_id": None
    },
    {
        "id": 40,
        "name_eng": "CCIN",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": "Waterloo",
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 41,
        "name_eng": "Institute of Oceanology, Sopot. Polish Academy of Sciences",
        "name_fre": None,
        "abbrev": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "location_id": None
    },
    {
        "id": 42,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "Mactaquac Biodiversity Facility",
        "city": "French Village",
        "postal_code": "E3E 2C6",
        "location_id": None
    },
    {
        "id": 43,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "200 Kent ST.",
        "city": "Ottawa",
        "postal_code": "K1A 0E6",
        "location_id": None
    },
    {
        "id": 44,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "24 Industrial Drive",
        "city": "Seabrook",
        "postal_code": "B0V 1A0",
        "location_id": None
    },
    {
        "id": 45,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "Mersey Biodiversity Facility",
        "city": "Milton",
        "postal_code": "B0T1P0",
        "location_id": None
    },
    {
        "id": 46,
        "name_eng": "NRCAN",
        "name_fre": None,
        "abbrev": None,
        "address": "1 Challenger Drive, P.O. Box 1006, 5th Floor, Room: M513B",
        "city": "Dartmouth",
        "postal_code": "B2Y 4A2",
        "location_id": None
    },
    {
        "id": 47,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "850 Route de la Mer",
        "city": "Mont-Joli",
        "postal_code": "G5H 3Z4",
        "location_id": 14
    },
    {
        "id": 48,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "80 East White Hills Rd",
        "city": "St. John's",
        "postal_code": "A1C 5X1",
        "location_id": 8
    },
    {
        "id": 49,
        "name_eng": "Government of Canada; Fisheries and Oceans Canada",
        "name_fre": "Gouvernement du Canada; Pêches et Océans Canada",
        "abbrev": "DFO-MPO",
        "address": "1 Regent Square",
        "city": "Corner Brook",
        "postal_code": "A2H 7K6",
        "location_id": 8
    }
]


def get_choices():
    return [(item["id"], f'{item["name_eng"]} ({item["city"]})') for item in object_list]


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
