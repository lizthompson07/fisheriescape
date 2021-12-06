import csv
import os
from copy import deepcopy

import pytz
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import make_aware

from lib.functions.custom_functions import listrify
from scuba import models



def check_samples():
    for s in models.Sample.objects.all():
        dive_transects = list(set([d.transect for d in s.dives.all()]))
        if len(dive_transects) > 1:
            print(s)

    for d in models.Dive.objects.all():
        if d.transect != d.sample.transect:
            print("big problemo")


def revamp_transects():
    # NOTHING TO DO WITH SPREADSHEET
    # let's attach the region directly to the transect; also, give the transect a new name based on site + transect name
    # for t in models.Transect.objects.all():
    #     if not t.region:
    #         t.region = t.site.region
    #     # if not t.old_name:
    #     try:
    #         t.old_name = f"{t.site.name}-{t.name}"
    #         t.new_name = f"{t.site.name}-{t.name}"
    #     except Exception as E:
    #         print(E, t)
    #     t.save()
    #
    # # let's attach the region directly to the sample as well; this is just temporarily while we figure out the whole transect thing.
    # for s in models.Sample.objects.all():
    #     if not s.region:
    #         s.region = s.site.region
    #         s.save()
    #
    # # actually, a sample should have only a single transect associated with it.
    # for s in models.Sample.objects.all():
    #     dive_transects = list(set([d.transect for d in s.dives.all()]))
    #     if not s.transect:
    #         # let's start with the easy one. If there is only one transect across all the dives, we only have to populate the sample's transect field and then we are done.
    #         if len(dive_transects) == 1:
    #             s.transect = dive_transects[0]
    #             s.save()
    #         # otherwise, we will have to duplicate the samples
    #         elif len(dive_transects) > 1:
    #             # take the first transect and use for the current sample
    #             s.transect = dive_transects[0]
    #             s.save()
    #
    #             # next, go through the unique list of transects. make sure a sample exists for each.
    #             for t in dive_transects:
    #                 sample_qs = models.Sample.objects.filter(datetime=s.datetime, transect=t)
    #                 # if this sample does not exist, clone from the original
    #                 if not sample_qs.exists():
    #                     new_sample = deepcopy(s)
    #                     new_sample.pk = None
    #                     new_sample.transect = t
    #                     new_sample.save()
    #                 else:
    #                     new_sample = sample_qs.first()
    #
    #                 # go though the dives of the original sample and move over any that need to be moved
    #                 if not s == new_sample:
    #                     for d in s.dives.all():
    #                         if new_sample.transect == d.transect:
    #                             d.sample = new_sample
    #                             d.save()

    # open the csv we want to read

    # my_target_data_file = os.path.join(settings.BASE_DIR, 'scuba', 'data', 'scuba revamp1.csv')
    # with open(my_target_data_file, 'r') as csv_read_file:
    #     my_csv = csv.DictReader(csv_read_file)
    #     for row in my_csv:
    #         # clean the dict:
    #         for key in row:
    #             if row[key] == "---":
    #                 row[key] = None
    #
    #         # see if we can match the region
    #         region_name = row["region"]
    #         region_qs = models.Region.objects.filter(name__iexact=region_name)
    #         region = None
    #         if not region_qs.exists():
    #             print(region_name, "region not found.")
    #         elif region_qs.count() > 1:
    #             print(region_name, "has too many matches.")
    #         else:
    #             region = region_qs.first()
    #
    #         if region:
    #             transect_qs = region.transects.filter(old_name=row["old_name"])
    #             if not transect_qs.exists():
    #                 print(row["old_name"], "not found in", region)
    #             elif transect_qs.count() > 1:
    #                 print(row["old_name"], "found multiple times in", region)
    #             else:
    #                 t = transect_qs.first()
    #                 t.name = row["transect_New"]
    #                 t.save()

    # go through each region and move over all the samples from duplicate transects
    for r in models.Region.objects.all():
        transects = r.transects.all()
        for t0 in transects:
            try:
                dup_qs = transects.filter(name=t0.name)
                if dup_qs.count() > 1:
                    print(listrify([t.old_name for t in dup_qs]), f"to be combined into one transect called '{dup_qs.first().name}'")

            #         keeper = None
            #         # keep the one that has coordinates
            #         for t1 in dup_qs:
            #             if t1.has_coordinates:
            #                 keeper = t1
            #                 break
            #             keeper = t1
            #
            #         # go through the other transects that will not be kept and move over samples.
            #         deletables = dup_qs.filter(~Q(id=keeper.id))
            #         for t1 in deletables:
            #             for s in t1.samples.all():
            #                 s.transect = keeper
            #                 s.save()
            #             if not t1.old_name in keeper.old_name:
            #                 keeper.old_name += f", {t1.old_name}"
            #                 keeper.save()
            #             t1.delete()
            except Exception as E:
                print(E, t0)









def populate_default():
    default_spp = get_object_or_404(models.Species, is_default=True)
    for o in models.Observation.objects.filter(species__isnull=True):
        o.species = default_spp
        o.save()


def is_number_tryexcept(s):
    """ Returns True is string is a number. https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float """
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def digest_data():
    small_length_mm = 60
    canner_length_mm = 75
    market_length_mm = 85

    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'scuba', 'diving_data_v2.csv')
    with open(my_target_data_file, 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)
        for row in my_csv:
            # clean the dict:
            for key in row:
                if row[key] == "NA":
                    row[key] = None

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
                AB1="Anse-Bleue",
                GA1="Grande-Anse",
                AB2="Anse-Bleue",
                GA2="Grande-Anse",
                SH="Shediac",
                CR="Caraquet",
                RI="Richibucto",
            )
            region_abbrev = row['Region']
            region_name = region_dict[region_abbrev]  # we want to crash is nothing is found.
            qs = models.Region.objects.filter(name=region_name)
            if qs.exists():
                region = qs.first()
            else:
                region = models.Region.objects.create(name=region_name, abbreviation=region_abbrev)

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
            year = int(row['Annee'])
            month = int(row['Mois'])
            day = int(row['Jour'])
            dt = make_aware(timezone.datetime(year, month, day), timezone=pytz.timezone("Canada/Atlantic"))
            sample, created = models.Sample.objects.get_or_create(
                site=site, datetime=dt, is_upm=bool(int(row['UPM']))
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
                rvienneau="Réjean Vienneau",
                sleblanc="Stépan Leblanc",
                slevesque="Sylvie Lévesque",
                yhache="Yvon Haché",
                phanley="Patricia Hanley",
                krobertson="Karen Robertson",
                nasselin="Natalie Asselin",
                marcouellet="Marc Ouellet",
                mgodin="M Godin",
            )

            mushed_name = row['Plongeur'].lower().strip()
            name = diver_dict[mushed_name]
            diver, created = models.Diver.objects.get_or_create(
                first_name=name.split(" ")[0], last_name=name.split(" ")[1]
            )
            # DIVE
            heading_txt = row['Heading'].lower() if row['Heading'] else None
            side_txt = row['Side'].lower() if row['Side'] else None
            heading = heading_txt[0] if heading_txt else None
            side = side_txt[0] if side_txt else None

            # there is a tricky things with the was_seeded tag
            # there were data entry errors and sometimes sections within the same dive will have conflicting reports
            # in talking with Bruno and Eliane, we determined that if a section == True, all sections within a dive should == True
            dive, created = models.Dive.objects.get_or_create(
                sample=sample,
                diver=diver,
                transect=transect,
                heading=heading,
                side=side,
                width_m=row['Width.m'],
            )

            # a one way change filter. The latter part of this correction will come downstream
            # if a dive was considered seeded at any point, it should always be considered seeded.
            was_seeded = bool(int(row['MartinMallet']))
            if was_seeded and not dive.was_seeded:
                dive.was_seeded = True
                dive.save()

            # SECTION
            section = None
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
                    depth_ft=row['Depth_.ft.'] if row['Depth_.ft.'] and is_number_tryexcept(row['Depth_.ft.']) else None,
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
                section = models.Section.objects.get(
                    dive=dive,
                    interval=row['section'],
                    # depth_ft=row['Depth_.ft.'] if is_number_tryexcept(row['Depth_.ft.']) else None,
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
            if section:
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

                # first trying getting length from the LC field
                length_txt_orig = row['LC_.mm.']
                length_txt = row['LC_.mm.'].strip().replace("?", "").replace("~", "").replace("±", "") if row['LC_.mm.'] else None
                escape_length_txt_orig = row['Escape']
                escape_length_txt = row['Escape'].strip().replace("?", "").replace("~", "").replace("±", "").replace("<", "").lower() if row['Escape'] else None
                length = None
                rough_estimate = False

                if is_number_tryexcept(length_txt):
                    length = float(length_txt)

                # if not successful, let's look to the Escape field
                if not length and escape_length_txt_orig:

                    length = None
                    if is_number_tryexcept(escape_length_txt):
                        length = float(escape_length_txt)
                    elif "can" in escape_length_txt:
                        length = canner_length_mm
                        rough_estimate = True
                    elif escape_length_txt in ["mar", "market"]:
                        length = market_length_mm
                        rough_estimate = True
                    elif "small" in escape_length_txt or "petit" in escape_length_txt:
                        length = small_length_mm
                        rough_estimate = True

                    # if the length is 1, it should just be set to null
                    if length == 1:
                        length = None

                if length:
                    # uncertainty
                    certainty = 1
                    # will deem the observation uncertain if there is a tilda in the lenth OR length is > 20 and sex is not known.
                    certainty_reason = None
                    if escape_length_txt_orig and ("~" in escape_length_txt_orig or "±" in escape_length_txt_orig or "<" in escape_length_txt_orig):
                        certainty = 0
                        certainty_reason = "Observation deemed uncertain because of tilda (or other approximation symbol) in length field."
                    elif length > 20 and sex == 'u':
                        certainty = 0
                        certainty_reason = "Observation deemed uncertain because > 20mm but sex is not known."
                    elif rough_estimate:
                        certainty = 0
                        certainty_reason = "Observation deemed uncertain length was described in qualitative terms. The import script used the following " \
                                           "conversion: Small=60mm; Canner=75mm; Market=85mm."

                    comment = f"Imported from MS Excel on {timezone.now().strftime('%Y-%m-%d')}. Original data: sex={sex_txt_orig}, " \
                              f"length={length_txt_orig}, escape={escape_length_txt_orig}."
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
                    comment = f"Row in excel spreadsheet did not result in an observation. Here is the original data: sex={sex_txt_orig}, " \
                              f"length={length_txt_orig}, escape={escape_length_txt_orig}"
                    if section.comment:
                        section.comment = f"ORIGINAL COMMENT: {section.comment}; {comment}"
                    else:
                        section.comment = comment
                    section.save()

    # some corrections...
    # if there was a sample-transect that has a one dive that was seeded, they should all be seeded.
    for sample in models.Sample.objects.filter(dives__was_seeded=True).distinct():
        for dive in sample.dives.filter(was_seeded=True):
            # find any other dives from the sample with the same transect and set to True as well
            for d in sample.dives.filter(was_seeded=False, transect=dive.transect):
                d.was_seeded = True
                d.save()


def delete_all_data():
    models.Sample.objects.filter(datetime__year__lte=2018).delete()
    # models.Transect.objects.all().delete()
    # models.Site.objects.all().delete()
    # models.Region.objects.all().delete()
    # models.Diver.objects.all().delete()
