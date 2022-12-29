from django.urls import path

from .views import SearchView, Index, AcronymView, DataGlossaryView,BusinessGlossaryView, DetailView, loadData, loadAcronyms


app_name = "pacificsalmondatahub"

# Map views to url paths here.
# as_view() is needed when using class-based views. 
urlpatterns = [
    path('', Index.as_view(), name = 'Index'),
    path('search/', SearchView.as_view(), name = 'search'),
    # Currently loading a static details page
    path('search/details/', DetailView.as_view(), name = 'details'),
    path('search/<str:uuid>/', DetailView.as_view(), name="search_detail_uuid"),    
    path('acronyms/', AcronymView.as_view(), name = 'acronym_list'),
    path('dataGlossary/', DataGlossaryView.as_view(), name = 'data_glossary_list'),
    path('businessGlossary/', BusinessGlossaryView.as_view(), name = 'business_glossary_list'),
    path('importcsv/', loadData, name = 'loadPSSIcsv'),
    path('getAC/', loadAcronyms, name = "loadAcronyms" )
]


