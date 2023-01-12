import os
import uuid

from django.db import models
from shared_models import models as shared_models
# Choices for language
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import default_if_none
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from shared_models.models import SimpleLookup, Region
from django.utils.translation import gettext as _
# Create your models here.

LANGUAGE_CHOICES = ((1, "English"), (2, "French"),)
YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]

#------------User Table--------------------
# Purpose: Stores users and associated access permissions
# Input: Can be used for permission/user-specific functions, not implemented yet
# Output: Stringify
#-------------------------------------------------
class InventoryUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pssiDataAsset_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="pssiDataAsset_users", on_delete=models.CASCADE, blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False, verbose_name=_("national administrator?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


#------------Data Asset Table--------------------
# Purpose: Store structured data from the data inventory spreadsheets
# Input: Data from inventory CSV file, imported with -> scripts/importCSV.py
# NOTE: Tags aka topics will be assigned to records within the inventory CSV, if a field is added in DataAsset table for topics, the Tag table can be removed
# Output: Stringify
#-------------------------------------------------

class DataAsset(models.Model):
    uuid = models.UUIDField(blank=True, null=True, verbose_name ="UUID", unique=True, default=uuid.uuid4)
    inventory_id = models.IntegerField(null=True, verbose_name="Inventory ID")
    approved_by = models.CharField(max_length=25, null=True, verbose_name="Approved By")
    data_asset_name = models.CharField(max_length=255, null=True, verbose_name="Data Asset Name")
    data_asset_steward = models.CharField(max_length=255, null=True, verbose_name="Data Asset Steward")
    data_asset_sorting_category = models.IntegerField(null=True, blank =True, verbose_name="Data Asset Sorting Category")
    operational_or_analytical_data = models.CharField(max_length=25, null=True, verbose_name="Operational Or Analytical Data")
    data_asset_acronym = models.CharField(max_length=50, null=True, verbose_name="Data Asset Acronym")
    data_asset_description = models.TextField(blank =True, null=True, verbose_name="Data Asset Description")
    apm_id = models.IntegerField(blank =True, null=True, verbose_name="apm_id")
    non_salmon_data = models.CharField(max_length=50, null=True, verbose_name="Non Salmon Data")
    data_asset_status = models.CharField(max_length=25, null=True, verbose_name="Data Asset Status")
    data_asset_format = models.CharField(max_length=255, null=True, verbose_name="Data Asset Format")
    data_type = models.CharField(max_length=50, null=True, verbose_name="Data Type")
    data_asset_location = models.CharField(max_length=50, null=True, verbose_name="Data Asset Location")
    data_asset_trustee = models.CharField(max_length=255, null=True, verbose_name="Data Asset Trustee")
    data_asset_custodian = models.CharField(max_length=255, null=True, verbose_name="Data Asset Custodian")
    application_data_asset_is_associated_with = models.TextField(blank =True, null=True, verbose_name="Application Data Asset is Associated With")
    application_description = models.TextField(blank =True, null=True, verbose_name="Application Description")
    technical_documentation = models.TextField(blank =True, null=True, verbose_name="Technical Documentation")
    access_point = models.TextField(blank =True, null=True, verbose_name="Access Point")
    policy_levers_data_asset_supports = models.CharField(max_length=50, null=True, verbose_name="Policy Levers Data Asset Supports")
    key_decisions = models.TextField(blank =True, null=True, verbose_name="Key Decisions")
    impact_to_dfo_data_consumers = models.CharField(max_length=255, null=True, verbose_name="Impact to DFO Data Consumers")
    decision_supporting_key_products = models.TextField(null=True, blank =True, verbose_name="Decision Supporting Key Products")
    impact_on_decision_making = models.CharField(max_length=255, null=True, verbose_name="Impact on Decision Making")
    uniqueness = models.CharField(max_length=50, null=True, verbose_name="Uniqueness")
    cost = models.CharField(max_length=50, null=True, verbose_name="Cost")
    data_asset_size = models.TextField(blank =True, null=True, verbose_name="Data Asset Size")
    update_frequency = models.CharField(max_length=50, null=True, verbose_name="Update Frequency")
    data_standards = models.CharField(max_length=50, null=True, verbose_name="Data Standards")
    metadata_maturity = models.CharField(max_length=50, null=True, verbose_name="Metadata Maturity")
    data_quality_rating = models.CharField(max_length=50, null=True, verbose_name="Data Quality Rating")
    naming_conventions = models.CharField(max_length=50, null=True, verbose_name="Naming Conventions")
    security_classification = models.CharField(max_length=50, null=True, verbose_name="Security Classification")
    inbound_data_linkage = models.TextField(blank =True, null=True, verbose_name="Inbound Data Linkage")
    outbound_data_linkage = models.TextField(blank =True, null=True, verbose_name="Outbound Data Linkage")
    publication_status = models.TextField(blank =True, null=True, verbose_name="Publication Status")

    # Defines DataAsset records/instances by their Data Asset Name e.g. record could be saved in Django model as "Fishery Operation System" instead of "DataAsset Object(1)"
    # NOTE: It is the same for other models -> to change the attribute the object is defined with, change the string with the field name
    def __str__(self):
        return "{}".format(getattr(self, str(_("data_asset_name"))))


#---------------Tags/Topics Table-----------------
# Purpose: Store topics for records in DataAsset - primary_tag_ID allows for a hierarchy of tag i.e. primary tags vs. subtags
# Input: Topic field in data inventory CSV -> this table may not be needed if there is one topic for each record
#        Feel free to comment out this table if you decide to use a topics field in DataAsset model instead
# Output: Stringify
#-------------------------------------------------
class Tag(models.Model):
    tag_id = models.IntegerField()
    tag_name = models.CharField(max_length=255)
    primary_tag_id = models.IntegerField(blank =True, null=True)
    inventory_id = models.ManyToManyField(DataAsset, related_name="topic", verbose_name="Topic")

    # Automatically called when converting object to string
    def __str__(self):
        return "{}".format(getattr(self, str(_("tag_name"))))


#----------------Acronyms Table-------------------
# Purpose: Store acronyms and related info - Acronym page pulls values from this table
# Input: Data from acronym CSV file, imported with -> scripts/importAcronyms.py
# Output: Stringify
#-------------------------------------------------
class Acronym(models.Model):
    acronym_id = models.IntegerField(null=True)
    acronym_letters = models.CharField(max_length=50, null=True, verbose_name="Acronym")
    acronym_full_name = models.CharField(max_length=255, verbose_name="Meaning of the Acronym")
    acronym_topic = models.CharField(max_length=255, blank=True, null=True, verbose_name="Categories and Tags")
    acronym_url = models.URLField(blank=True, null=True, verbose_name="Link to Acronym Source")

    def __str__(self):
        return "{}".format(getattr(self, str(_("acronym_letters"))))


#------------Data Glossary Table-----------------
# Purpose: Contains names and descriptions for data related glossary terms within a detail page
#          Data Glossary Page pulls data from this table
# Input: Data Glossary CSV file -> script to pull data not implemented yet
# Output: Stringify
#-------------------------------------------------      
class DataGlossary(models.Model):
    data_glossary_id = models.IntegerField()
    term_name = models.CharField(max_length=255)
    term_description = models.TextField()
    inventory_id = models.ManyToManyField(DataAsset)


#------------Business Glossary Table-----------------
# Purpose: Contains names and descriptions for data related glossary terms within a detail page
#          Business Glossary Page pulls data from this table 
# Input: Business Glossary CSV file -> script to pull data not implemented yet
# Output: Stringify
#----------------------------------------------------
class BusinessGlossary(models.Model):
    business_glossary_id = models.IntegerField()
    term_name = models.CharField(max_length=255)
    term_description = models.TextField()
    inventory_id = models.ManyToManyField(DataAsset)

#------------------Comments Table--------------------
# Purpose: Stores comments/concerns left by users and the info needed to reach out to them
# Input: Comments from users (function to process comments not implemented yet)
# Output: Stringify
#----------------------------------------------------
class Comment(models.Model):
    comment_id = models.IntegerField()
    comment_creator = models.CharField(max_length=255, null=True)
    comment_contact_info = models.CharField(max_length=255, null=True)
    comment_subject = models.CharField(max_length=255)
    comment_contents = models.TextField()
    inventory_id = models.ForeignKey(DataAsset, on_delete=models.CASCADE)

