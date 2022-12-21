from django.urls import path

from .views import SearchView, Index, AcronymView, DataGlossaryView,BusinessGlossaryView, DetailView, loadData, loadAcronyms


app_name = "pssiDataInventory"

# Map views to url paths here
urlpatterns = [
    path('', Index.as_view(), name = 'Index'),
    path('search/', SearchView.as_view(), name = 'search'),
    path('search/details/', DetailView.as_view(), name = 'details'),
    path('acronyms/', AcronymView.as_view(), name = 'acronym_list'),
    path('dataGlossary/', DataGlossaryView.as_view(), name = 'data_glossary_list'),
    path('businessGlossary/', BusinessGlossaryView.as_view(), name = 'business_glossary_list'),
    path('importcsv/', loadData, name = 'loadPSSIcsv'),
    path('getAC/', loadAcronyms, name = "loadAcronyms" )
]


