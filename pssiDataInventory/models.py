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

LANGUAGE_CHOICES = ((1, 'English'), (2, 'French'),)
YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]

class InventoryUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pssiDataAsset_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="pssiDataAsset_users", on_delete=models.CASCADE, blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False, verbose_name=_("national administrator?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


#------------Data Asset Table-----------------
# Purpose: Store structured data from the data inventory spreadsheets
# Input: Data from inventory CSV file, imported with -> scripts/importCSV.py
# Output: Stringify
#-------------------------------------------------

class DataAsset(models.Model):
    uuid = models.UUIDField(blank=True, null=True, verbose_name = "UUID", unique=True)
    Inventory_ID = models.IntegerField()
    Approved_By = models.CharField(max_length = 50, null = True)
    Data_Asset_Name = models.CharField(max_length = 125, null = True)
    Data_Asset_Steward = models.CharField(max_length = 50, null = True)
    Data_Asset_Sorting_Category = models.IntegerField()
    Operational_Or_Analytical_Data = models.CharField(max_length = 15, null = True)
    Data_Asset_Acronym = models.CharField(max_length = 15, null = True)
    Data_Asset_Description = models.TextField(blank = True, null = True)
    APM_ID = models.IntegerField(blank = True, null = True)
    Non_Salmon_Data = models.CharField(max_length = 5, null = True)
    Data_Asset_Status = models.CharField(max_length = 25, null = True)
    Data_Asset_Format = models.CharField(max_length = 50, null = True)
    Data_Type = models.CharField(max_length = 15, null = True)
    Data_Asset_Location = models.CharField(max_length = 25, null = True)
    Data_Asset_Trustee = models.CharField(max_length = 50, null = True)
    Data_Asset_Custodian = models.CharField(max_length = 50, null = True)
    Application_Data_Asset_is_Associated_With = models.TextField(blank = True, null = True)
    Application_Description = models.TextField(blank = True, null = True)
    Technical_Documentation = models.TextField(blank = True, null = True)
    Access_Point = models.TextField(blank = True, null = True)
    Policy_Levers_Data_Asset_Supports = models.CharField(max_length = 25, null = True)
    Key_Decisions = models.TextField(blank = True, null = True)
    Impact_to_DFO_Data_Consumers = models.CharField(max_length = 125, null = True)
    Decision_Supporting_Key_Products = models.TextField()
    Impact_on_Decision_Making = models.CharField(max_length = 10, null = True)
    Uniqueness = models.CharField(max_length = 5, null = True)
    Cost = models.TextField(blank = True, null = True)
    Data_Asset_Size = models.TextField(blank = True, null = True)
    Update_Frequency = models.CharField(max_length = 25, null = True)
    Data_Standards = models.CharField(max_length = 50, null = True)
    Metadata_Maturity = models.CharField(max_length = 5, null = True)
    Data_Quality_Rating = models.CharField(max_length = 15, null = True)
    Naming_Conventions = models.CharField(max_length = 15, null = True)
    Security_Classification = models.CharField(max_length = 15, null = True)
    Inbound_Data_Linkage = models.TextField(blank = True, null = True)
    Outbound_Data_Linkage = models.TextField(blank = True, null = True)
    Publication_Status = models.TextField(blank = True, null = True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("Data_Asset_Name"))))


#---------------Tags/Topics Table-----------------
# Purpose: Store topics for records in DataAsset - primary_tag_ID allows for a hierarchy of tag i.e. primary tags vs. subtags
# Input: 
# Output: Stringify
#-------------------------------------------------
class Tag(models.Model):
    tag_ID = models.IntegerField()
    tag_Name = models.CharField(max_length = 25)
    primary_tag_ID = models.IntegerField(blank = True, null = True)
    InventoryID = models.ManyToManyField(DataAsset, related_name="topic")

    # Automatically called when converting object to string
    def __str__(self):
        return "{}".format(getattr(self, str(_("tag_Name"))))


#----------------Acronyms Table-------------------
# Purpose: Store acronyms and related info - Acronym page pulls values from this table
# Input: Data from acronym CSV file, imported with -> scripts/importAcronyms.py
# Output: Stringify
#-------------------------------------------------
class Acronym(models.Model):
    acronym_ID = models.CharField(max_length = 10)
    acronym_Full_Name = models.CharField(max_length = 100)
    acronym_Topic = models.CharField(max_length = 75, blank=True, null=True)
    acronym_URL = models.URLField(max_length = 50, blank = True, null = True)

    def __str__(self):
        return "{}".format(getattr(self, str(_("acronym_ID"))))


#------------Data Glossary Table-----------------
# Purpose: Contains names and descriptions for data related glossary terms within a detail page
#          Data Glossary Page pulls data from this table
# Input: 
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
# Input: 
# Output: Stringify
#----------------------------------------------------
class BusinessGlossary(models.Model):
    businessGlossary_ID = models.IntegerField()
    term_Name = models.CharField(max_length = 25)
    term_Description = models.TextField()
    Inventory_ID = models.ManyToManyField(DataAsset)

#------------------Comments Table--------------------
# Purpose: Contains names and descriptions for data related glossary terms within a detail page
#          Business Glossary Page pulls data from this table 
# Input: 
# Output: Stringify
#----------------------------------------------------
class Comment(models.Model):
    comment_ID = models.IntegerField()
    comment_Creator = models.CharField(max_length = 25, null = True)
    comment_ContactInfo = models.CharField(max_length = 50, null = True)
    comment_Subject = models.CharField(max_length = 50)
    comment_Contents = models.TextField()
    Inventory_ID = models.ForeignKey(DataAsset, on_delete = models.CASCADE )

