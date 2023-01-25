from shared_models.utils import dotdict

object_list = [
    {
        "id": 1,
        "title": "Dataset (CSV) - Bilingual",
        "english_value": "Dataset;CSV;eng,fra",
        "french_value": "Données;CSV;eng,fra"
    },
    {
        "id": 2,
        "title": "Dataset (CSV) - English",
        "english_value": "Dataset;CSV;eng",
        "french_value": "Données;CSV;eng"
    },
    {
        "id": 3,
        "title": "Dataset (CSV) - French ",
        "english_value": "Dataset;CSV;fra",
        "french_value": "Données;CSV;fra"
    },
    {
        "id": 4,
        "title": "ESRI Web Service - Bilingual ",
        "english_value": "Web Service;ESRI REST;eng,fra",
        "french_value": "Service Web;ESRI REST;eng,fra"
    },
    {
        "id": 5,
        "title": "ESRI Web Service - English",
        "english_value": "Web Service;ESRI REST;eng",
        "french_value": "Service Web;ESRI REST;eng"
    },
    {
        "id": 6,
        "title": "ESRI Web Service - French",
        "english_value": "Web Service;ESRI REST;fra",
        "french_value": "Service Web;ESRI REST;fra"
    },
    {
        "id": 7,
        "title": "Supporting Documentation (CSV) - Bilingual",
        "english_value": "Supporting Document;CSV;eng,fra",
        "french_value": "Document de soutien;CSV;eng,fra"
    },
    {
        "id": 8,
        "title": "Supporting Documentation (CSV) - English",
        "english_value": "Supporting Document;CSV;eng",
        "french_value": "Document de soutien;CSV;eng"
    },
    {
        "id": 9,
        "title": "Supporting Documentation (CSV) - French",
        "english_value": "Supporting Document;CSV;fra",
        "french_value": "Document de soutien;CSV;fra"
    },
    {
        "id": 10,
        "title": "Supporting Documentation (PDF) - Bilingual",
        "english_value": "Supporting Document;PDF;eng,fra",
        "french_value": "Document de soutien;PDF;eng,fra"
    },
    {
        "id": 11,
        "title": "Supporting Documentation (PDF) - English",
        "english_value": "Supporting Document;PDF;eng",
        "french_value": "Document de soutien;PDF;eng"
    },
    {
        "id": 12,
        "title": "Supporting Documentation (PDF) - French",
        "english_value": "Supporting Document;PDF;fra",
        "french_value": "Document de soutien;PDF;fra"
    },
    {
        "id": 13,
        "title": "Supporting Documentation (GeoJSON) - Bilingual",
        "english_value": "Supporting Document;GEOJSON;eng,fra",
        "french_value": "Document de soutien;GEOJSON;eng,fra"
    },
    {
        "id": 14,
        "title": "Supporting Documentation (GeoJSON) - English",
        "english_value": "Supporting Document;GEOJSON;eng",
        "french_value": "Document de soutien;GEOJSON;eng"
    },
    {
        "id": 15,
        "title": "Supporting Documentation (GeoJSON) - French",
        "english_value": "Supporting Document;GEOJSON;fra",
        "french_value": "Document de soutien;GEOJSON;fra"
    },
    {
        "id": 16,
        "title": "Supporting Documentation (ESRI FGDB) - Bilingual",
        "english_value": "Supporting Document;FGDB\/GDB;eng,fra",
        "french_value": "Document de soutien;FGDB\/GDB;eng,fra"
    },
    {
        "id": 17,
        "title": "Supporting Documentation (ESRI FGDB) - English",
        "english_value": "Supporting Document;FGDB\/GDB;eng",
        "french_value": "Document de soutien;FGDB\/GDB;eng"
    },
    {
        "id": 18,
        "title": "Supporting Documentation (ESRI FGDB) - French",
        "english_value": "Supporting Document;FGDB\/GDB;fra",
        "french_value": "Document de soutien;FGDB\/GDB;fra"
    },
    {
        "id": 19,
        "title": "Supporting Documentation (ESRI Shapefile) - Bilingual",
        "english_value": "Supporting Document;SHP;eng,fra",
        "french_value": "Document de soutien;SHP;eng,fra"
    },
    {
        "id": 20,
        "title": "Supporting Documentation (ESRI Shapefile) - English",
        "english_value": "Supporting Document;SHP;eng",
        "french_value": "Document de soutien;SHP;eng"
    },
    {
        "id": 21,
        "title": "Supporting Documentation (ESRI Shapefile) - French",
        "english_value": "Supporting Document;SHP;fra",
        "french_value": "Document de soutien;SHP;fra"
    },
    {
        "id": 22,
        "title": "Dataset (XLSX) - Bilingual",
        "english_value": "Dataset;XLSX;eng,fra",
        "french_value": "Données;XLSX;eng,fra"
    },
    {
        "id": 23,
        "title": "Dataset (XLSX) - English",
        "english_value": "Dataset;XLSX;eng",
        "french_value": "Données;XLSX;eng"
    },
    {
        "id": 24,
        "title": "Dataset (XLSX) - French ",
        "english_value": "Dataset;XLSX;fra",
        "french_value": "Données;XLSX;fra"
    },
    {
        "id": 25,
        "title": "Dataset (TIFF) - Bilingual",
        "english_value": "Dataset;TIFF;eng,fra",
        "french_value": "Données;TIFF;eng,fra"
    },
    {
        "id": 26,
        "title": "Dataset (TIFF) - English",
        "english_value": "Dataset;TIFF;eng",
        "french_value": "Données;TIFF;eng"
    },
    {
        "id": 27,
        "title": "Dataset (TIFF) - French ",
        "english_value": "Dataset;TIFF;fra",
        "french_value": "Données;TIFF;fra"
    },
    {
        "id": 28,
        "title": "Dataset (ZIP) - Bilingual",
        "english_value": "Dataset;ZIP;eng,fra",
        "french_value": "Données;ZIP;eng,fra"
    },
    {
        "id": 29,
        "title": "Dataset (ZIP) - English",
        "english_value": "Dataset;ZIP;eng",
        "french_value": "Données;ZIP;eng"
    },
    {
        "id": 30,
        "title": "Dataset (ZIP) - French ",
        "english_value": "Dataset;ZIP;fra",
        "french_value": "Données;ZIP;fra"
    },
    {
        "id": 31,
        "title": "Supporting Documentation (XLSX) - Bilingual",
        "english_value": "Supporting Document;XLSX;eng,fra",
        "french_value": "Document de soutien;XLSX;eng,fra"
    },
    {
        "id": 32,
        "title": "Supporting Documentation (XLSX) - English",
        "english_value": "Supporting Document;XLSX;eng",
        "french_value": "Document de soutien;XLSX;eng"
    },
    {
        "id": 33,
        "title": "Supporting Documentation (XLSX) - French",
        "english_value": "Supporting Document;XLSX;fra",
        "french_value": "Document de soutien;XLSX;fra"
    }
]


def get_choices():
    return [(item["id"], f'{item["title"]}') for item in object_list]


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
