from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # RIVER #
    #########
    path('rivers/', views.RiverListView.as_view(), name="river_list"),
    path('river/new/', views.RiverCreateView.as_view(), name="river_new"),
    path('river/<int:pk>/view/', views.RiverDetailView.as_view(), name="river_detail"),
    path('river/<int:pk>/edit/', views.RiverUpdateView.as_view(), name="river_edit"),
    path('river/<int:pk>/delete/', views.RiverDeleteView.as_view(), name="river_delete"),

    # RIVER SITE #
    ##############
    path('river/<int:river>/site/new/', views.RiverSiteCreateView.as_view(), name="site_new"),
    path('site/new/', views.RiverSiteCreateView.as_view(), name="site_new"),
    path('site/<int:pk>/view/', views.RiverSiteDetailView.as_view(), name="site_detail"),
    path('site/<int:pk>/edit/', views.RiverSiteUpdateView.as_view(), name="site_edit"),
    path('site/<int:pk>/delete/', views.RiverSiteDeleteView.as_view(), name="site_delete"),

    # SAMPLE #
    ##########
    path('samples/', views.SampleListView.as_view(), name="trap_list"),
    path('sample/new/', views.SampleCreateView.as_view(), name="trap_new"),
    path('sample/<int:pk>/view/', views.SampleDetailView.as_view(), name="trap_detail"),
    path('sample/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="trap_edit"),
    path('sample/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="trap_delete"),


    #
    #
    # # STATION #
    # ###########
    # path('site/<int:site>/new-station/', views.StationCreateView.as_view(), name="station_new"),
    # path('new-station/', views.NoSiteStationCreateView.as_view(), name="station_new"),
    # path('station/<int:pk>/view/', views.StationDetailView.as_view(), name="station_detail"),
    # path('station/<int:pk>/edit/', views.StationUpdateView.as_view(), name="station_edit"),
    # path('station/<int:pk>/delete/', views.StationDeleteView.as_view(), name="station_delete"),
    #
    # # SPECIES #
    # ###########
    # path('species/', views.SpeciesListView.as_view(), name="species_list"),
    # path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    # path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    # path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    # path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),
    #
    # # SPECIES OBSERVATIONS #
    # ########################
    # path('sample/<int:sample>/species/insert/', views.SpeciesObservationInsertView.as_view(),
    #      name="species_obs_search"),
    # path('sample/<int:sample>/species/<int:species>/add/', views.SpeciesObservationCreateView.as_view(),
    #      name="species_obs_new"),
    # path('species-observation/<int:pk>/edit/', views.SpeciesObservationUpdateView.as_view(), name="species_obs_edit"),
    # path('species-observation/<int:pk>/delete/return-to-<str:backto>/', views.species_observation_delete,
    #      name="species_obs_delete"),
    #
    # # Reports #
    # ###########
    # path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    # path('reports/<str:species_list>/species-count/', views.report_species_count, name="species_report"),
    # path('reports/species-richness/', views.report_species_richness, name="species_richness"),
    # path('reports/species-richness/site/<int:site>/', views.report_species_richness, name="species_richness"),
    # path('reports/annual-watershed-report/site/<int:site>/year/<int:year>',
    #      views.AnnualWatershedReportTemplateView.as_view(), name="watershed_report"),
    # path('reports/annual-watershed-spreadsheet/site/<int:site>/year/<int:year>', views.annual_watershed_spreadsheet,
    #      name="watershed_xlsx"),
    # path('reports/fgp-csv-export/', views.fgp_export, name="watershed_csv"),
    # path('reports/ais-export/species-list/<str:species_list>/', views.ais_export, name="ais_export"),

]

app_name = 'trapnet'
