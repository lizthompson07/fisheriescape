import os
from django.conf import settings
import unicodecsv as csv
from camp import models


def generate_fgp_export():
    # figure out the filename
    target_file = "fgp_camp_dataset.csv"
    target_file_path = os.path.join("C:\\users\\fishmand\\projects\\fgp-datasets\\", target_file)

    with open(target_file_path, 'wb') as csvfile:
        csvfile.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(csvfile, delimiter=',')
        # write the header
        writer.writerow([
            "year / année",
            "month / mois",
            "province",
            "site",
            "station",
            "latitude (n)",
            "longitude (w)",
            "start date / date de début",
            "end date / date de fin",
            "ammonia / ammoniac",
            "dissolved oxygen / oxygène dissous",
            "nitrates",
            "nitrite",
            "phosphate",
            "salinity / salinité",
            "silicate",
            "water temperature / température de l'eau (C)",
            "gravel / gravier (%)",
            "mud / boue (%)",
            "rock / roche (%)",
            "sand / sable (%)",
            "species name (English) / nom de l'espèce (anglais)",
            "species name (French) / nom de l'espèce (français)",
            "scientific name / nom scientifique",
            "ITIS TSN ID",
            "submerged aquatic vegetation (SAV) / végétation aquatique submergée (VAS)",
            "SAV level observed / VAS niveau observé",
            "adults / adultes",
            "young of the year / jeunes de l'année",
            "total number of individuals observed / total nombre d'individus observés",
        ])

        for obs in models.SpeciesObservation.objects.all():
            print(obs.id)
            writer.writerow(
                [
                    obs.sample.year,
                    obs.sample.month,
                    "{} - {}".format(obs.sample.station.site.province.province_eng, obs.sample.station.site.province.province_fre),
                    obs.sample.station.site.site,
                    obs.sample.station.name,
                    obs.sample.station.latitude_n,
                    obs.sample.station.longitude_w,
                    obs.sample.start_date,
                    obs.sample.end_date,
                    obs.sample.ammonia,
                    obs.sample.dissolved_o2,
                    obs.sample.nitrates,
                    obs.sample.nitrite,
                    obs.sample.phosphate,
                    obs.sample.salinity,
                    obs.sample.silicate,
                    obs.sample.h2o_temperature_c,
                    obs.sample.percent_gravel,
                    obs.sample.percent_mud,
                    obs.sample.percent_rock,
                    obs.sample.percent_sand,
                    obs.species.common_name_eng,
                    obs.species.common_name_fre,
                    obs.species.scientific_name,
                    obs.species.tsn,
                    obs.species.sav,
                    obs.adults,
                    obs.yoy,
                    obs.total_non_sav,
                    obs.total_sav,
                ])
        return None

