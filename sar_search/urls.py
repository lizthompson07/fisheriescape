from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # SPECIES #
    ###########
    path('species/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),
    #
    # # RIVER #
    # #########
    # path('rivers/', views.RiverListView.as_view(), name="river_list"),
    # path('river/new/', views.RiverCreateView.as_view(), name="river_new"),
    # path('river/<int:pk>/view/', views.RiverDetailView.as_view(), name="river_detail"),
    # path('river/<int:pk>/edit/', views.RiverUpdateView.as_view(), name="river_edit"),
    # path('river/<int:pk>/delete/', views.RiverDeleteView.as_view(), name="river_delete"),
    #
    # # RIVER SITE #
    # ##############
    # path('river/<int:river>/site/new/', views.RiverSiteCreateView.as_view(), name="site_new"),
    # path('site/new/', views.RiverSiteCreateView.as_view(), name="site_new"),
    # path('site/<int:pk>/view/', views.RiverSiteDetailView.as_view(), name="site_detail"),
    # path('site/<int:pk>/edit/', views.RiverSiteUpdateView.as_view(), name="site_edit"),
    # path('site/<int:pk>/delete/', views.RiverSiteDeleteView.as_view(), name="site_delete"),
    #
    # # SAMPLE #
    # ##########
    # path('samples/', views.SampleListView.as_view(), name="trap_list"),
    # path('sample/new/', views.SampleCreateView.as_view(), name="trap_new"),
    # path('sample/<int:pk>/view/', views.SampleDetailView.as_view(), name="trap_detail"),
    # path('sample/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="trap_edit"),
    # path('sample/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="trap_delete"),
    #
    # # ENTRY #
    # #########
    # path('sample/<int:sample>/entry/insert/', views.EntryInsertView.as_view(), name="obs_insert"),
    # path('sample/<int:sample>/new-entry/add/species/<int:species>/', views.EntryCreateView.as_view(), name="obs_new"),
    # path('entry/<int:pk>/edit/', views.EntryUpdateView.as_view(), name="obs_edit"),
    # path('entry/<int:pk>/delete/', views.species_observation_delete, name="obs_delete"),
    #
    # # Reports #
    # ###########
    # path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    # path('reports/samples/<str:year>/<str:sites>/', views.export_sample_data, name="sample_report"),
    # path('reports/entries/<str:year>/<str:sites>/', views.export_entry_data, name="entry_report"),
    # path('reports/opendata1/<str:year>/<str:sites>/', views.export_open_data_ver1, name="od1_report"),

]

app_name = 'sar_search'
