import csv
import os

import pytz
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from django.utils.timezone import make_aware

from scuba import models


def is_number_tryexcept(s):
    """ Returns True is string is a number. https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float """
    try:
        float(s)
        return True
    except ValueError:
        return False


def digest_data():
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'scuba', '2019_data_import.csv')
    with open(my_target_data_file, 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            # REGION
            region_dict = dict(
                AB="Anse-Bleue",
                CG="Cocagne (aka God’s place)",
                CQ="Caraquet",
                FH="Fox Harbor",
                GA="Grande-Anse",
                MC="Murray Corner",
                NG="Neguac",
                PH="Pigeon Hill",
                PV="Pointe-Verte",
                RB="Richibucto",
                RO="Robichaud",
                SC="Shediac",
                TB="Tabusintac",
                TR="Toney River",
            )
            region_abbrev = row['Region']
            region_name = region_dict[region_abbrev]  # we want to crash is nothing is found.
            region, created = models.Region.objects.get_or_create(name=region_name, abbreviation=region_abbrev)

            # SITE
            site_name = row['Site'].upper()
            site, created = models.Site.objects.get_or_create(
                name=site_name, abbreviation=site_name, region=region
            )

            # TRANSECT
            transect_name = row['Transect'].upper()
            transect, created = models.Transect.objects.get_or_create(
                name=transect_name, site=site
            )

            # SAMPLE
            year = int(row['Année'])
            month = int(row['Mois'])
            day = int(row['Jour'])
            dt = make_aware(timezone.datetime(year, month, day), timezone=pytz.timezone("Canada/Atlantic"))
            sample, created = models.Sample.objects.get_or_create(
                site=site, datetime=dt
            )

            # DIVER
            diver_dict = dict(
                arondeau="Amélie Rondeau",
                bcomeau="Bruno Comeau",
                dgiard="David Giard",
                elandry="Éric Landry",
                fplante="François Plante",
                fsavoie="Fernand Savoie",
                glandry="Germain Landry",
                gpaulin="Gilles Paulin",
                grobichaud="Guy Robichaud",
                mcomeau="Michel Comeau",
                mcousino="Maryse Cousineau",
                mouellet="Maxime Ouellet",
                rdoucette="Renelle Doucette",
                rfrigo="Renaud Frigault",
                rvienneau=" Réjean Vienneau",
                sleblanc="Stépan Leblanc",
                slevesque="Sylvie Lévesque",
                yhache="Yvon Haché",
                phanley="Patricia Hanley",
                krobertson="Karen Robertson",
                nasselin="Natalie Asselin",
            )

            mushed_name = row['Plongeur'].lower().strip()
            name = diver_dict[mushed_name]
            diver, created = models.Diver.objects.get_or_create(
                first_name=name.split(" ")[0], last_name=name.split(" ")[1]
            )

            # DIVE
            heading_txt = row['Heading'].lower()
            side_txt = row['Side'].lower()
            heading = heading_txt[0] if not heading_txt[0] == "u" else None
            side = side_txt[0] if not side_txt[0] == "u" else None

            dive, created = models.Dive.objects.get_or_create(
                sample=sample,
                diver=diver,
                transect=transect,
                heading=heading,
                side=side,
                width_m=row['Width (m)'],
            )

            # SECTION
            sand = float(row['Sa']) if is_number_tryexcept(row['Sa']) else 0
            mud = float(row['Va']) if is_number_tryexcept(row['Va']) else 0
            hard = float(row['Du']) if is_number_tryexcept(row['Du']) else 0
            algae = float(row['Al']) if is_number_tryexcept(row['Al']) else 0
            gravel = float(row['Gr']) if is_number_tryexcept(row['Gr']) else 0
            cobble = float(row['Co']) if is_number_tryexcept(row['Co']) else 0
            pebble = float(row['Ca']) if is_number_tryexcept(row['Ca']) else 0

            try:
                section, created = models.Section.objects.get_or_create(
                    dive=dive,
                    interval=row['section'],
                    depth_ft=row['Depth_(ft)'] if is_number_tryexcept(row['Depth_(ft)']) else None,
                    comment=row['Comments'],

                    percent_sand=sand,
                    percent_mud=mud,
                    percent_hard=hard,
                    percent_algae=algae,
                    percent_gravel=gravel,
                    percent_cobble=cobble,
                    percent_pebble=pebble,

                )
            except IntegrityError as E:
                # comment = row[
                #               'Comments'] + f"; There is a problem with the source data: the diver's description of substrate is not consistent between observations (rows)"
                section = models.Section.objects.get(
                    dive=dive,
                    interval=row['section'],
                    depth_ft=row['Depth_(ft)'] if is_number_tryexcept(row['Depth_(ft)']) else None,
                )
                section_comment = "There is a problem with the source data: the diver's description of substrate is not consistent between observations (rows)"
                if not section.comment:
                    section.comment = section_comment
                elif section_comment in section.comment:
                    pass
                else:
                    section.comment += f'; {section_comment}'
                section.save()

                dive_comment = f"There is a problem with the source data: the diver's description of substrate is not " \
                                       f"consistent between observations (rows): please see section interval #{row['section']}"
                if not dive.comment:
                    dive.comment = dive_comment
                elif dive_comment in dive.comment:
                    pass
                else:
                    dive.comment += f'; {dive_comment}'

                dive.save()
                # print(E, section, dive)

            # OBSERVATIONS
            # sex
            sex_txt_orig = row['sexe']
            sex_txt = row['sexe'].lower().strip().replace(" ", "").replace("-", "")
            sex = None
            if sex_txt in ["m", "f"]:
                sex = sex_txt
            else:
                sex = 'u'

            egg_status = None
            if sex_txt in ["b", "b1", "b2", "b3", "b4"]:
                egg_status = sex_txt
                sex = 'f'

            length_txt_orig = row['LC_(mm)']
            length_txt = row['LC_(mm)'].strip().replace("?", "").replace("~", "")
            length = None
            if is_number_tryexcept(length_txt):
                length = float(length_txt)

            if length:
                # uncertainty
                certainty = 1
                # will deem the observation uncertain if there is a tilda in the lenth OR length is > 20 and sex is not known.
                certainty_reason = None
                if "~" in row['LC_(mm)']:
                    certainty = 0
                    certainty_reason = "Observation deemed uncertain because of tilda in length field."
                elif length > 20 and sex == 'u':
                    certainty = 0
                    certainty_reason = "Observation deemed uncertain because > 20mm but sex is not known."

                comment = f"Imported from MS Excel on {timezone.now().strftime('%Y-%m-%d')}. Original data: sex={sex_txt_orig}, length={length_txt_orig}."
                if certainty_reason:
                    comment += f" {certainty_reason}"

                models.Observation.objects.create(
                    section=section,
                    sex=sex,
                    egg_status=egg_status,
                    carapace_length_mm=length,
                    comment=comment,
                    certainty_rating=certainty,
                )

            else:
                # lets make a comment about this entry in the section
                comment = f"Row in excel spreadsheet did not result in an observation. Here is the original data: sex={sex_txt_orig}, length={length_txt_orig}"
                if section.comment:
                    section.comment += f"; {comment}"
                else:
                    section.comment = comment
                section.save()


def delete_all_data():
    models.Sample.objects.all().delete()
    models.Transect.objects.all().delete()
    models.Site.objects.all().delete()
    models.Region.objects.all().delete()
