from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from . import models


def is_nat_admin(user):
    if user:
        return bool(hasattr(user, "inventory_user") and user.inventory_user.is_admin)


def is_regional_admin(user):
    if user:
        return bool(hasattr(user, "inventory_user") and user.inventory_user.region)


def is_admin(user):
    return is_nat_admin(user) or is_regional_admin(user)


def is_custodian(user, resource):
    if user.id:
        # if the user has no associated Person in the app, automatic fail
        try:
            person, created = models.Person.objects.get_or_create(user=user)
            if created:
                print("creating person!!")
        except ObjectDoesNotExist:
            return False
        else:
            # check to see if they are listed as custodian (role_id=1) on the specified resource id
            # custodian (1); principal investigator (2); data manager (8); steward (19); author (13); owner (10)
            return models.ResourcePerson.objects.filter(person=person, resource=resource,
                                                        role_id__in=[1, 2, 8, 19, 13, 10]).count() > 0


def can_modify(user, resource_id, as_dict=False):
    resource = get_object_or_404(models.Resource, pk=resource_id)
    can_modify = False
    reason = _("You did not get clearance.")

    if is_nat_admin(user):
        can_modify = True
        reason = _("As an national administrator of this application, you have the necessary permissions to modify this record.")
    elif is_regional_admin(user) and resource.section and resource.section.division.branch.sector.region == user.inventory_user.region:
        can_modify = True
        reason = _("As a {region} region administrator, you have the necessary permissions to modify this record.").format(region=user.inventory_user.region)
    elif is_custodian(user, resource):
        can_modify = True
        reason = _("Your role on this record gives you the necessary permissions to modify this record.")

    if as_dict:
        payload = dict(can_modify=can_modify, reason=reason)
        return payload
    else:
        return can_modify


def can_modify_dma(user, dma_id, as_dict=False):
    dma = get_object_or_404(models.DMA, pk=dma_id)

    can_modify = False
    reason = _("You are not authorized to make changes to this record.")

    if is_nat_admin(user):
        can_modify = True
        reason = _("As an national administrator of this application, you have the necessary permissions to modify this record.")
    elif is_regional_admin(user) and dma.section and dma.section.division.branch.sector.region == user.inventory_user.region:
        can_modify = True
        reason = _("As a {region} region administrator, you have the necessary permissions to modify this record.").format(region=user.inventory_user.region)
    elif user in [dma.data_contact, dma.metadata_contact, dma.created_by]:
        can_modify = True
        reason = _("Your role on this record gives you the necessary permissions to modify this record.")

    if as_dict:
        payload = dict(can_modify=can_modify, reason=reason)
        return payload
    else:
        return can_modify


def get_resource_field_list():
    my_list = [
        "section",
        "title_eng",
        "title_fre",
        "purpose_eng",
        "purpose_fre",
        "descr_eng",
        "descr_fre",
        "notes",
        "resource_type",
        "status",
        "maintenance",
        "maintenance_text",
        "time_period|time period",
        # "time_start_month",
        # "time_start_year",
        # "time_end_day",
        # "time_end_month",
        # "time_end_year",
        "geo_descr_eng",
        "geo_descr_fre",
        # "west_bounding",
        # "south_bounding",
        # "east_bounding",
        # "north_bounding",
        "security_classification",
        "security_use_limitation_eng",
        "security_use_limitation_fre",
        "parent",
        "distribution_formats",
        "data_char_set",
        "spat_representation",
        "spat_ref_system",
        "resource_constraint_eng",
        "resource_constraint_fre",
        "sampling_method_eng",
        "sampling_method_fre",
        "physical_sample_descr_eng",
        "physical_sample_descr_fre",
        "qc_process_descr_eng",
        "qc_process_descr_fre",
        "parameters_collected_eng",
        "parameters_collected_fre",
        "analytic_software",
        "additional_credit",
        "storage_solutions",
        "storage_solution_text",
        "storage_needed",
        "raw_data_retention",
        "data_retention",
        "backup_plan",
        "cloud_costs",
        "had_sharing_agreements",
        "sharing_agreements_text",
        "publication_timeframe",
        "publishing_platforms",
        "sharing_comments",
        # "fgp_url",
        # "public_url",
        # "thumbnail_url",
        # "fgp_publication_date",
        # "od_publication_date",
        # "od_release_date",
        # "last_revision_date",
        "open_data_notes",
        # "uuid",
        # "review_status",
        # "date_last_modified",
        # "last_modified_by",
    ]
    return my_list


def get_dma_field_list():
    my_list = [
        'title',
        'data_contact',
        'metadata_contact',
        'metadata_tool',
        'metadata_url',
        'metadata_update_freq',
        'metadata_freq_text',
        'storage_solutions',
        'storage_solution_text',
        'storage_needed',
        'raw_data_retention',
        'data_retention',
        'backup_plan',
        'cloud_costs',
        'had_sharing_agreements',
        'sharing_agreements_text',
        'publication_timeframe',
        'publishing_platforms',
        'comments',
        'status',
        'metadata',
    ]
    return my_list


def get_dma_review_field_list():
    my_list = [
        'fiscal_year',
        'decision_display|{}'.format("decision"),
        'comments',
        'metadata|{}'.format("metadata"),
    ]
    return my_list
