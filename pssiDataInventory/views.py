from django.shortcuts import render

from django.db.models import Value, TextField, Q, Count
from django.db.models.functions import Concat
from django.utils.translation import gettext as _, gettext_lazy
# Create your views here.
from .models import DataAsset, Tag, Acronym
from . import filters
from .mixins import PSSIDataInventoryBasicMixin
from .scripts.importCSV import clearInventory, run_csvToInventory
from .scripts.importAcronyms import clear, run
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonFilterView, CommonDetailView, CommonListView, \
    CommonUpdateView, CommonCreateView, CommonPopoutCreateView, CommonPopoutDeleteView, CommonPopoutUpdateView, CommonDeleteView


class Index(PSSIDataInventoryBasicMixin, CommonTemplateView):
    template_name = 'pssiDataInventory/index.html'
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Center")
    active_page_name_crumb = gettext_lazy("Home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class SearchView(PSSIDataInventoryBasicMixin, CommonFilterView):

    filterset_class = filters.pssiFilter
    template_name = 'pssiDataInventory/list.html'
    queryset = DataAsset.objects.order_by("Inventory_ID").annotate(
        search_term=Concat('Data_Asset_Name', Value(" "),
                           'Data_Asset_Steward', Value(" "),
                           'Data_Asset_Acronym', Value(" "),
                           'Inventory_ID', Value(" "),
                           'Data_Asset_Description',
                           output_field=TextField()))
    home_url_name = "pssiDataInventory:Index"
    container_class = "container-fluid"
    row_object_url_name = "pssiDataInventory:resource_detail"
    #new_object_url = reverse_lazy("pssiDataInventory:resource_detail")
    #paginate_by = 25
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['tagName'] = Tag.tag_Name
        

    #     return context

    # Change displayed fields here ("name": "<fieldName>")
    field_list = [
        {"name": 'Data_Asset_Name', "class": "", "width": ""},
        {"name": 'Data_Asset_Acronym', "class": "", "width": ""},
        {"name": 'Data_Asset_Description', "class": "w-50", "width": ""},
        {"name": 'Data_Asset_Steward', "class": "", "width": ""},
        {"name": 'topic', "class": "", "width": ""},
    ]

class AcronymView(PSSIDataInventoryBasicMixin, CommonTemplateView):
    template_name = 'pssiDataInventory/acronym_list.html'
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Center - Acronyms")
    active_page_name_crumb = gettext_lazy("Acronyms")
    home_url_name = "pssiDataInventory:Index"

    # row_object_url_name = "pssiDataInventory:data_detail"
    # paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = Acronym.objects.all()
        context['list'] = object_list
        return context

    field_list = [
        {"name": 'acronym_ID', "class": "my-0 term", "width": ""},
        {"name": 'acronym_Full_Name', "class": "description", "width": ""},
    ]

class DataGlossaryView(PSSIDataInventoryBasicMixin, CommonTemplateView):
    template_name = 'pssiDataInventory/data_glossary_list.html'
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Center - Data Glossary")
    active_page_name_crumb = gettext_lazy("Data Glossary")
    home_url_name = "pssiDataInventory:Index"
    # row_object_url_name = "pssiDataInventory:data_detail"
    # paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class BusinessGlossaryView(PSSIDataInventoryBasicMixin, CommonTemplateView):
    template_name = 'pssiDataInventory/business_glossary_list.html'
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Center - Business Glossary")
    active_page_name_crumb = gettext_lazy("Business Glossary")
    home_url_name = "pssiDataInventory:Index"
    # row_object_url_name = "pssiDataInventory:data_detail"
    # paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class DetailView(PSSIDataInventoryBasicMixin, CommonTemplateView):
    template_name = 'pssiDataInventory/details_page.html'
    h1 = gettext_lazy("PSSI - Pacific Salmon Data Center - Details")
    active_page_name_crumb = gettext_lazy("Details")
    home_url_name = "pssiDataInventory:Index"
    # row_object_url_name = "pssiDataInventory:data_detail"
    # paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

def loadData(request):
    clearInventory()
    run_csvToInventory()

    if(DataAsset):
        return HttpResponse("Success!")
    else:
        return HttpResponse("No data found.")

def loadAcronyms(request):
    clear()
    run()

    if(Acronym):
        return HttpResponse("Success!")
    else:
        return HttpResponse("No data found.")