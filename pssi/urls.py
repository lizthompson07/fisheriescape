from django.urls import path

from .views import SearchView, Index, AcronymView, DataGlossaryView,BusinessGlossaryView, DetailView, load_data, load_acronyms, load_business_glossary, load_data_glossary, load_data_pandas


app_name = "pssi"

# Map views to url paths here.
# as_view() is needed when using class-based views. 
urlpatterns = [
    path("", Index.as_view(), name = "index"),

    # SEARCH & DATA HUB DETAILS
    path("search/", SearchView.as_view(), name = "search"),
    path("datahub/view/<int:pk>/", DetailView.as_view(), name="details"),
    path("datahub/<str:uuid>/", DetailView.as_view(), name="details_uuid"),
    path("datahub/<int:pk>/<str:data_asset_name>/", DetailView.as_view(), name="details_data_asset_name"),

    # DATA HUB MANAGEMENT
    # path('datahub/new/', DataHubCreateView.as_view(), name="datahub_new"),
    # path('datahub/edit/<int:pk>/', DataHubUpdateView.as_view(), name="datahub_edit"),
    # path('datahub/delete/<int:pk>', DataHubDeleteView.as_view(), name="datahub_delete"),

    # INFORMATIONS
    path("acronyms/", AcronymView.as_view(), name = "acronym_list"),
    path("dataglossary/", DataGlossaryView.as_view(), name = "data_glossary_list"),
    path("businessglossary/", BusinessGlossaryView.as_view(), name = "business_glossary_list"),

    # IMPORTING CSV
    path("importcsv/", load_data, name = "load_pssi_csv"),
    path("importcsvpandas/", load_data_pandas, name = "load_pssi_csv_pandas"),
    path("importacronyms/", load_acronyms, name = "load_acronyms"),
    path("importdataglossary/", load_data_glossary, name = "load_data_glossary"),
    path("importbusinessglossary/", load_business_glossary, name = "load_business_glossary"),
]