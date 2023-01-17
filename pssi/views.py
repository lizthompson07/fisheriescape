from django.shortcuts import render

from django.db.models import Value, TextField, Q, Count
from django.db.models.functions import Concat
from django.utils.translation import gettext as _, gettext_lazy
# Create your views here.
from .models import DataAsset, Tag, Acronym, DataGlossary, BusinessGlossary
from . import filters
from .mixins import PSSIBasicMixin
from .scripts.import_csv import clear_inventory, run_csv_to_inventory
from .scripts.import_acronyms import clear as clear_acronyms, run as run_acronyms
from .scripts.import_business_glossary import clear as clear_business_glossary, run as run_business_glossary
from .scripts.import_data_glossary import clear as clear_data_glossary, run as run_data_glossary
from .scripts.import_csv_pandas import clear as clear_inventory_pandas, run as run_csv_to_inventory_pandas

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonFilterView, CommonDetailView, CommonListView, \
    CommonUpdateView, CommonCreateView, CommonPopoutCreateView, CommonPopoutDeleteView, CommonPopoutUpdateView, CommonDeleteView

#------------------Index/Home View--------------------
# Purpose: Act as central hub for users to navigate to different pages on our site. This is the home page.
# Input:Reads from index.html using the CommonTemplateView from shared_models/views.py
# Output: Index page with redirect links to various pages of our project
#----------------------------------------------------
class Index(PSSIBasicMixin, CommonTemplateView):
    # Define which html file this view uses here
    template_name = "pssi/index.html"
    # Header at the top of the page
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Hub")
    # Name for button in breadcrumbs(top-left of page)
    active_page_name_crumb = gettext_lazy("Home")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


#------------------Search View-----------------------
# Purpose: Allow users to search for specific data assets using keywords or other filters
# Input: Reads from search_list.html(which extends search.html) using the CommonFilterView from shared_models/views.py
#        Pulls data from DataAsset model in the get_context_data() method
# Output: Records in a list with redirect links to their respective detail pages
#----------------------------------------------------
class SearchView(PSSIBasicMixin, CommonFilterView):

    filterset_class = filters.pssiFilter
    template_name = "pssi/search_list.html"
    queryset = DataAsset.objects.order_by("inventory_id").annotate(
        search_term=Concat("data_asset_name", Value(" "),
                           "data_asset_steward", Value(" "),
                           "data_asset_acronym", Value(" "),
                           "inventory_id", Value(" "),
                           "data_asset_description",
                           output_field=TextField()))
    home_url_name = "pssi:index"
    container_class = "container-fluid"
    row_object_url_name = "pssi:details"

    # Uncomment this line when detail page has been set up. When clicking on record in Search Page, this URL will redirect to details page
    # NOTE: pssi:<name_of_page> accesses the url with name = "<name_of_page>" in the arguments of path()
    new_object_url = reverse_lazy("pssi:details")

    # If implementing pagination, this defines how many results per page
    #paginate_by = 25
    
    # Currently not doing anything - if there are variables in HTML files, this is where to define the values to pass in
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        

        return context

    # Change displayed fields for the list in search page here ("name": "<fieldName>")
    field_list = [
        {"name": "data_asset_name", "class": "", "width": ""},
        {"name": "data_asset_acronym", "class": "", "width": ""},
        {"name": "data_asset_description", "class": "w-50", "width": ""},
        {"name": "data_asset_steward", "class": "", "width": ""},
        {"name": "topic", "class": "", "width": ""},
    ]

#------------------Acronym View--------------------
# Purpose: Display a list of departmental acronyms and their meanings. 
# Input: Reads from acronym_list.html using the CommonTemplateView from shared_models/views.py
#        Pulls data from Acronym model in the get_context_data() method
# Output: List of acronyms, separated by first letter of the acronyms. Clicking on acronym can lead to information source page.
#----------------------------------------------------
class AcronymView(PSSIBasicMixin, CommonTemplateView):
    model = Acronym
    template_name = "pssi/acronym_list.html"
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Hub - Acronyms")
    active_page_name_crumb = gettext_lazy("Acronyms")
    home_url_name = "pssi:index"

    # Define list (variable in acronym_list.html) as all objects in the Acronym table
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.model.objects.all()

        # Define dynamic category list
        unique_list = []
        field_name = "acronym_letters"
        for object in context["object_list"]:
            category_letter = getattr(object, field_name)[0].upper()
            if category_letter not in unique_list:
                unique_list.append(category_letter)
        context["categories"] = "".join(unique_list)
        
        return context

    # Fields to display in acronym page - values for class are used for styling/formatting data
    field_list = [
        {"name": "acronym_letters", "class": "my-0 term", "width": ""},
        {"name": "acronym_full_name", "class": "description", "width": ""},
    ]

#------------------Data Glossary View----------------
# Purpose: Will display data-related glossary terms, their descriptions, and sources
# Input:Reads from data_glossary.html using the CommonTemplateView from shared_models/views.py
#       When making the page dynamic, pull data from DataGlossary model
# Output: Same page structure as acronym view, but displays data glossary information
#----------------------------------------------------
class DataGlossaryView(PSSIBasicMixin, CommonTemplateView):
    model = DataGlossary
    template_name = "pssi/data_glossary_list.html"
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Hub - Data Glossary")
    active_page_name_crumb = gettext_lazy("Data Glossary")
    home_url_name = "pssi:index"
    # row_object_url_name = "pssi:data_detail"
    # paginate_by = 25

    # Define list (variable in acronym_list.html) as all objects in the Acronym table
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.model.objects.all()

        # Define dynamic category list
        unique_list = []
        field_name = "term_name"
        for object in context["object_list"]:
            category_letter = getattr(object, field_name)[0].upper()
            if category_letter not in unique_list:
                unique_list.append(category_letter)
        context["categories"] = "".join(unique_list)
        
        return context

#----------------Business Glossary View--------------
# Purpose:Will display business-related glossary terms, their descriptions, and sources
# Input:Reads from business_glossary.html using the CommonTemplateView from shared_models/views.py
#       When making the page dynamic, pull data from BusinessGlossary model
# Output:Same page structure as acronym view, but displays data glossary information
#----------------------------------------------------
class BusinessGlossaryView(PSSIBasicMixin, CommonTemplateView):
    model = BusinessGlossary
    template_name = "pssi/business_glossary_list.html"
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Hub - Business Glossary")
    active_page_name_crumb = gettext_lazy("Business Glossary")
    home_url_name = "pssi:index"
    # row_object_url_name = "pssi:data_detail"
    # paginate_by = 25

    # Define list (variable in acronym_list.html) as all objects in the Acronym table
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.model.objects.all()

        # Define dynamic category list
        unique_list = []
        field_name = "term_name"
        for object in context["object_list"]:
            category_letter = getattr(object, field_name)[0].upper()
            if category_letter not in unique_list:
                unique_list.append(category_letter)
        context["categories"] = "".join(unique_list)
        
        return context

#------------------Detail View--------------------
# Purpose: When clicking on object in Search View, redirect to this view
# Input: Reads from details_page.html using the CommonTemplateView from shared_models/views.py
# Output: Two-column page to display DataAsset fields. List of anchors on the left side of the screen.
#----------------------------------------------------
class DetailView(PSSIBasicMixin, CommonDetailView):
    model = DataAsset
    template_name = "pssi/details_page.html"
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Hub - Details")
    active_page_name_crumb = gettext_lazy("Details")
    home_url_name = "pssi:index"
    # row_object_url_name = "pssi:data_detail"
    # paginate_by = 25

    def get_object(self, queryset=None):
        if self.kwargs.get("uuid"):
            return get_object_or_404(self.model, uuid=self.kwargs.get("uuid"))
        return super().get_object(queryset)
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self.kwargs.get("uuid"):
            return HttpResponseRedirect(reverse("pssi:details_uuid", kwargs={"uuid": obj.uuid}))

        # xml_export.verify(obj)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["topics"] = [obj.topics]

        # Dictionary for data stewards contacts
        data_stewards_contact_collection = []
        emails = []

        for item in obj.contact_email.split(";"):
            item = item.strip()
            if item != "":
                emails.append(item)

        for item in obj.data_asset_steward.split(";"):
            if item == "":
                continue
            else:
                item = item.title()
                
            if "," in item:
                lname, fname = item.split(",", 1)
                lname = lname.strip()
                fname = fname.strip()
            else:
                lname = item
                fname = ""
                
            email = ""
            for e in emails:
                if lname != "":
                    if lname in e:
                        email = e
                        break
                        
            data_stewards_contact_collection.append({
                "lname" : lname,
                "fname" : fname,
                "email" : email
            })
        # for item in obj.contact_email.split(";"):
        #     item = item.strip()
        #     emails.append(item)
        # for item in obj.data_asset_steward.split(";"):
        #     item = item.title()
        #     if "," in item:
        #         lname, fname = item.split(",", 1)
        #         lname = lname.strip()
        #         fname = fname.strip()
        #     else:
        #         lname = item
        #         fname = ""
        #     for email in emails:
        #         if lname != "":
        #             if lname in email:
        #                 data_stewards_contact_collection.append({
        #                     "lname" : lname,
        #                     "fname" : fname,
        #                     "email" : email
        #                 })
        context["data_stewards_contact_collection"] = data_stewards_contact_collection
        

        return context


#--------------Functions--------------------------
# NOTE: These just run the scripts in the scripts folder to clear out the models and populate them with CSV files
# These are currently run by entering their URLs (Lines 16-17 of urls.py), please find a more secure process to run these scripts
#-------------------------------------------------
def load_data(request):
    clear_inventory()
    run_csv_to_inventory()

    if(DataAsset):
        return HttpResponse("Success!")
    else:
        return HttpResponse("No data found.")

def load_acronyms(request):
    clear_acronyms()
    run_acronyms()

    if(Acronym):
        return HttpResponse("Success!")
    else:
        return HttpResponse("No data found.")

def load_data_glossary(request):
    clear_data_glossary()
    # run_data_glossary()

    if(DataGlossary):
        return HttpResponse("Success!")
    else:
        return HttpResponse("No data found.")

def load_business_glossary(request):
    clear_business_glossary()
    # run_business_glossary()

    if(BusinessGlossary):
        return HttpResponse("Success!")
    else:
        return HttpResponse("No data found.")

def load_data_pandas(request):
    # clear_inventory_pandas()
    run_csv_to_inventory_pandas()

    if(DataAsset):
        return HttpResponse("Success!")
    else:
        return HttpResponse("No data found.")