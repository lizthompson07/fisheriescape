from django.urls import path

from .views import SearchView, Index, AcronymView, DataGlossaryView,BusinessGlossaryView, DetailView, loadData, loadAcronyms, loadBusinessGlossary, loadDataGlossary


app_name = "pacificsalmondatahub"

# Map views to url paths here.
# as_view() is needed when using class-based views. 
urlpatterns = [
    path('', Index.as_view(), name = 'Index'),

    # SEARCH LIST AND DETAILS
    path('search/', SearchView.as_view(), name = 'search'),
    path('search/<int:pk>/view/', DetailView.as_view(), name="details"),
    path('search/<str:uuid>/', DetailView.as_view(), name="details_uuid"),
    path('search/details/', DetailView.as_view(), name = 'details_static'),

    path('acronyms/', AcronymView.as_view(), name = 'acronym_list'),
    path('dataglossary/', DataGlossaryView.as_view(), name = 'data_glossary_list'),
    path('businessglossary/', BusinessGlossaryView.as_view(), name = 'business_glossary_list'),

    # IMPORTING CSV
    path('importcsv/', loadData, name = 'load_pssi_csv'),
    path('importacronyms/', loadAcronyms, name = "load_acronyms"),
    path('importdataglossary/', loadDataGlossary, name = "load_data_glossary"),
    path('importbusinessglossary/', loadBusinessGlossary, name = "load_business_glossary"),
]