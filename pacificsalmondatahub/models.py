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
    uuid = models.UUIDField(blank=True, null=True, verbose_name = "UUID", unique=True, default=uuid.uuid4)
    Inventory_ID = models.IntegerField(null=True, verbose_name="Inventory ID")
    Approved_By = models.CharField(max_length = 50, null = True, verbose_name="Approved By")
    Data_Asset_Name = models.CharField(max_length = 125, null = True, verbose_name="Data Asset Name")
    Data_Asset_Steward = models.CharField(max_length = 50, null = True, verbose_name="Data Asset Steward")
    Data_Asset_Sorting_Category = models.IntegerField(null = True, blank = True, verbose_name="Data Asset Sorting Category")
    Operational_Or_Analytical_Data = models.CharField(max_length = 15, null = True, verbose_name="Operational Or Analytical Data")
    Data_Asset_Acronym = models.CharField(max_length = 15, null = True, verbose_name="Data Asset Acronym")
    Data_Asset_Description = models.TextField(blank = True, null = True, verbose_name="Data Asset Description")
    APM_ID = models.IntegerField(blank = True, null = True, verbose_name="APM_ID")
    Non_Salmon_Data = models.CharField(max_length = 5, null = True, verbose_name="Non Salmon Data")
    Data_Asset_Status = models.CharField(max_length = 25, null = True, verbose_name="Data Asset Status")
    Data_Asset_Format = models.CharField(max_length = 50, null = True, verbose_name="Data Asset Format")
    Data_Type = models.CharField(max_length = 15, null = True, verbose_name="Data_Type")
    Data_Asset_Location = models.CharField(max_length = 25, null = True, verbose_name="Data Asset Location")
    Data_Asset_Trustee = models.CharField(max_length = 50, null = True, verbose_name="Data Asset Trustee")
    Data_Asset_Custodian = models.CharField(max_length = 50, null = True, verbose_name="Data Asset Custodian")
    Application_Data_Asset_is_Associated_With = models.TextField(blank = True, null = True, verbose_name="Application Data Asset is Associated With")
    Application_Description = models.TextField(blank = True, null = True, verbose_name="Application Description")
    Technical_Documentation = models.TextField(blank = True, null = True, verbose_name="Technical Documentation")
    Access_Point = models.TextField(blank = True, null = True, verbose_name="Access Point")
    Policy_Levers_Data_Asset_Supports = models.CharField(max_length = 25, null = True, verbose_name="Policy Levers Data Asset Supports")
    Key_Decisions = models.TextField(blank = True, null = True, verbose_name="Key Decisions")
    Impact_to_DFO_Data_Consumers = models.CharField(max_length = 125, null = True, verbose_name="Impact to DFO Data Consumers")
    Decision_Supporting_Key_Products = models.TextField(null = True, blank = True, verbose_name="Decision Supporting Key Products")
    Impact_on_Decision_Making = models.CharField(max_length = 10, null = True, verbose_name="Impact on Decision Making")
    Uniqueness = models.CharField(max_length = 5, null = True, verbose_name="Uniqueness")
    Cost = models.TextField(blank = True, null = True, verbose_name="Cost")
    Data_Asset_Size = models.TextField(blank = True, null = True, verbose_name="Data Asset Size")
    Update_Frequency = models.CharField(max_length = 25, null = True, verbose_name="Update Frequency")
    Data_Standards = models.CharField(max_length = 50, null = True, verbose_name="Data Standards")
    Metadata_Maturity = models.CharField(max_length = 5, null = True, verbose_name="Metadata Maturity")
    Data_Quality_Rating = models.CharField(max_length = 15, null = True, verbose_name="Data Quality Rating")
    Naming_Conventions = models.CharField(max_length = 15, null = True, verbose_name="Naming Conventions")
    Security_Classification = models.CharField(max_length = 15, null = True, verbose_name="Security Classification")
    Inbound_Data_Linkage = models.TextField(blank = True, null = True, verbose_name="Inbound Data Linkage")
    Outbound_Data_Linkage = models.TextField(blank = True, null = True, verbose_name="Outbound Data Linkage")
    Publication_Status = models.TextField(blank = True, null = True, verbose_name="Publication Status")

    # Defines DataAsset records/instances by their Data Asset Name e.g. record could be saved in Django model as "Fishery Operation System" instead of "DataAsset Object(1)"
    # NOTE: It is the same for other models -> to change the attribute the object is defined with, change the string with the field name
    def __str__(self):
        return "{}".format(getattr(self, str(_("Data_Asset_Name"))))


#---------------Tags/Topics Table-----------------
# Purpose: Store topics for records in DataAsset - primary_tag_ID allows for a hierarchy of tag i.e. primary tags vs. subtags
# Input: Topic field in data inventory CSV -> this table may not be needed if there is one topic for each record
#        Feel free to comment out this table if you decide to use a topics field in DataAsset model instead
# Output: Stringify
#-------------------------------------------------
class Tag(models.Model):
    tag_ID = models.IntegerField()
    tag_Name = models.CharField(max_length = 25)
    primary_tag_ID = models.IntegerField(blank = True, null = True)
    InventoryID = models.ManyToManyField(DataAsset, related_name="topic", verbose_name="Topic")

    # Automatically called when converting object to string
    def __str__(self):
        return "{}".format(getattr(self, str(_("tag_Name"))))


#----------------Acronyms Table-------------------
# Purpose: Store acronyms and related info - Acronym page pulls values from this table
# Input: Data from acronym CSV file, imported with -> scripts/importAcronyms.py
# Output: Stringify
#-------------------------------------------------
class Acronym(models.Model):
    acronym_ID = models.IntegerField(null = True)
    acronym_Letters = models.CharField(max_length = 10, null = True)
    acronym_Full_Name = models.CharField(max_length = 100)
    acronym_Topic = models.CharField(max_length = 75, blank=True, null=True)
    acronym_URL = models.URLField(max_length = 120, blank = True, null = True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("acronym_Letters"))))


#------------Data Glossary Table-----------------
# Purpose: Contains names and descriptions for data related glossary terms within a detail page
#          Data Glossary Page pulls data from this table
# Input: Data Glossary CSV file -> script to pull data not implemented yet
# Output: Stringify
#-------------------------------------------------      
class DataGlossary(models.Model):
    dataGlossary_ID = models.IntegerField()
    term_Name = models.CharField(max_length = 25)
    term_Description = models.TextField()
    Inventory_ID = models.ManyToManyField(DataAsset)


#------------Business Glossary Table-----------------
# Purpose: Contains names and descriptions for data related glossary terms within a detail page
#          Business Glossary Page pulls data from this table 
# Input: Business Glossary CSV file -> script to pull data not implemented yet
# Output: Stringify
#----------------------------------------------------
class BusinessGlossary(models.Model):
    businessGlossary_ID = models.IntegerField()
    term_Name = models.CharField(max_length = 25)
    term_Description = models.TextField()
    Inventory_ID = models.ManyToManyField(DataAsset)

#------------------Comments Table--------------------
# Purpose: Stores comments/concerns left by users and the info needed to reach out to them
# Input: Comments from users (function to process comments not implemented yet)
# Output: Stringify
#----------------------------------------------------
class Comment(models.Model):
    comment_ID = models.IntegerField()
    comment_Creator = models.CharField(max_length = 25, null = True)
    comment_ContactInfo = models.CharField(max_length = 50, null = True)
    comment_Subject = models.CharField(max_length = 50)
    comment_Contents = models.TextField()
    Inventory_ID = models.ForeignKey(DataAsset, on_delete = models.CASCADE )

