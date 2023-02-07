import os

from django.core import serializers
from django.core.files import File

from inventory import models
from inventory import xml_export
from shared_models import models as shared_models


def export_fixtures():
    """ a simple function to expor the important lookup tables. These fixutre will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../fixtures')
    models_to_export = [
        models.Location,
        models.Status,

        models.PersonRole,
        models.SpatialRepresentationType,
        models.SpatialReferenceSystem,
        models.SecurityClassification,
        models.ResourceType,
        models.Maintenance,
        models.CharacterSet,
        models.KeywordDomain,
        models.ContentType,
        shared_models.FiscalYear,
    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w')
        myfile = File(f)
        myfile.write(data)
        myfile.close()


def transfer_dist_formats():
    for resource in models.Resource.objects.filter(distribution_format__isnull=False):
        # look for match in other table
        df = models.DistributionFormat.objects.get(name__iexact=resource.distribution_format)
        resource.distribution_formats.add(df)


def resave_all(resources=models.Resource.objects.all()):
    for r in resources:
        xml_export.verify(r)


def import_new_species():
    pass
    # open the csv we want to read
    # rootdir = "C:\\Users\\fishmand\\Desktop\\dump"
    # with open(os.path.join(rootdir, "OntarioFishList.csv"), 'r') as csv_read_file:
    #     my_csv = csv.DictReader(csv_read_file)
    #
    #     for row in my_csv:
    #         tsn = row["TSN"]
    #         if tsn:
    #             # first check to make sure there is not a duplicate entry
    #             if models.Keyword.objects.filter(keyword_domain_id=2, uid=tsn).count() > 0:
    #                 my_kw = models.Keyword.objects.filter(keyword_domain_id=2, uid=tsn).first()
    #                 print("Keyword #{} already has TSN {}".format(my_kw.id, tsn))
    #             else:
    #                 # enter a new keyword
    #                 scientific_name = row["Scientific"]
    #                 common_names = row["common names"]
    #                 new_keyword = models.Keyword.objects.create(
    #                     text_value_eng=scientific_name,
    #                     text_value_fre=scientific_name,
    #                     uid=tsn,
    #                     concept_scheme='species',
    #                     details=common_names,
    #                     is_taxonomic=1,
    #                     keyword_domain_id=2,
    #                 )
    #         else:
    #             # enter a new keyword
    #             scientific_name = row["Scientific"]
    #             common_names = row["common names"]
    #             new_keyword = models.Keyword.objects.create(
    #                 text_value_eng=scientific_name,
    #                 text_value_fre=scientific_name,
    #                 concept_scheme='species',
    #                 details=common_names,
    #                 is_taxonomic=1,
    #                 keyword_domain_id=4,
    #             )
    #             print("'{}' does not have a TSN therefore is being added under the 'uncontrolled vocabulary' keyword domain".format(common_names))


def populate_resource_people2():
    for rp in models.ResourcePerson.objects.all():
        rp2, created = models.ResourcePerson2.objects.get_or_create(
            resource=rp.resource,
            user=rp.person.user
        )

        # transfer notes if this is being created for the first time
        if created:
            if rp.notes and len(rp.notes):
                if rp2.notes and len(rp2.notes):
                    rp2.notes += "; " + rp.notes
                else:
                    rp2.notes = rp.notes

        # add the org
        rp2.organization = rp.person.organization
        rp2.save()

        # add the roles
        rp2.roles.add(rp.role)

        # now lets compare the persons
        person1 = rp.person
        person2 = rp2.user.profile


        if not person2.phone and person1.phone:
            person2.phone = person1.phone
        if not person2.position_eng and person1.position_eng:
            person2.position_eng = person1.position_eng
        if not person2.position_fre and person1.position_fre:
            person2.position_fre = person1.position_fre
        person2.save()


def clear_nullstrings():
    for r in models.Resource.objects.all():
        for field in r._meta.fields:
            if "string" in field.description.lower() or "text" in field.description.lower():
                if getattr(r, field.name)is not None and getattr(r, field.name).strip() == "":
                    setattr(r, field.name, None)
                    r.save()



def migrate_DMAs():
    for dma in models.DMA.objects.filter(resource__isnull=False):
        print(dma.id, dma)
        resource = dma.resource
        # step 1, copy over any fields that should be copied over.
        ## start with the easy ones. The ones that do not exist in the new table

        for item in dma.storage_solutions.all():
            resource.storage_solutions.add(item)
        resource.storage_solution_text = dma.storage_solution_text
        resource.storage_needed = dma.storage_needed

        resource.raw_data_retention = dma.raw_data_retention
        resource.data_retention = dma.data_retention
        resource.backup_plan = dma.backup_plan
        resource.cloud_costs = dma.cloud_costs
        resource.sharing_agreements_text = dma.sharing_agreements_text
        resource.publication_timeframe = dma.publication_timeframe
        resource.publishing_platforms = dma.publishing_platforms
        resource.had_sharing_agreements = 1 if dma.had_sharing_agreements else 0
        resource.sharing_comments = dma.comments

        if resource.maintenance_text and dma.metadata_freq_text:
            resource.maintenance_text += "\n\n " + dma.metadata_freq_text
        elif dma.metadata_freq_text:
            resource.maintenance_text = dma.metadata_freq_text

        if dma.metadata_update_freq == 4:
            resource.maintenance = 6
        elif dma.metadata_update_freq == 5:
            resource.maintenance = 8
        elif dma.metadata_update_freq == 9:
            resource.maintenance = 8

        resource.save()

        # now lets look at reviews
        for old_review in dma.reviews.all():
            new_review, created = models.Review.objects.get_or_create(resource=resource, fiscal_year=old_review.fiscal_year)
            new_review.decision = old_review.decision
            new_review.is_final_review = old_review.is_final_review
            new_review.comments = old_review.comments
            new_review.created_by = old_review.created_by
            new_review.updated_by = old_review.updated_by
            new_review.created_at = old_review.created_at
            new_review.updated_at = old_review.updated_at
            new_review.save()

        dma.delete()





