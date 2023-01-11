from django.urls import path

from .views import SearchView, Index, AcronymView, DataGlossaryView,BusinessGlossaryView, DetailView, load_data, load_acronyms, load_business_glossary, load_data_glossary


app_name = "pacificsalmondatahub"

# Map views to url paths here.
# as_view() is needed when using class-based views. 
urlpatterns = [
    path("", Index.as_view(), name = "Index"),

    # SEARCH LIST AND DETAILS
    path("search/", SearchView.as_view(), name = "search"),
    path("search/<int:pk>/view/", DetailView.as_view(), name="details"),
    path("search/<str:uuid>/", DetailView.as_view(), name="details_uuid"),
    path("search/details/", DetailView.as_view(), name = "details_static"),

    path("acronyms/", AcronymView.as_view(), name = "acronym_list"),
    path("dataglossary/", DataGlossaryView.as_view(), name = "data_glossary_list"),
    path("businessglossary/", BusinessGlossaryView.as_view(), name = "business_glossary_list"),

    # IMPORTING CSV
    path("importcsv/", load_data, name = "load_pssi_csv"),
    path("importacronyms/", load_acronyms, name = "load_acronyms"),
    path("importdataglossary/", load_data_glossary, name = "load_data_glossary"),
    path("importbusinessglossary/", load_business_glossary, name = "load_business_glossary"),
]