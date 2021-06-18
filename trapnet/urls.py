from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # SETTINGS #
    ############
    path('settings/statuses/', views.StatusFormsetView.as_view(), name="manage_statuses"),
    path('settings/status/<int:pk>/delete/', views.StatusHardDeleteView.as_view(), name="delete_status"),
    path('settings/sexes/', views.SexFormsetView.as_view(), name="manage_sexes"),
    path('settings/sexes/<int:pk>/delete/', views.SexHardDeleteView.as_view(), name="delete_sex"),
    path('settings/life-stages/', views.LifeStageFormsetView.as_view(), name="manage_life_stages"),
    path('settings/life-stage/<int:pk>/delete/', views.LifeStageHardDeleteView.as_view(), name="delete_life_stage"),
    path('settings/origins/', views.OriginFormsetView.as_view(), name="manage_origins"),
    path('settings/origin/<int:pk>/delete/', views.OriginHardDeleteView.as_view(), name="delete_origin"),
    path('settings/maturities/', views.MaturityFormsetView.as_view(), name="manage_maturities"),
    path('settings/maturities/<int:pk>/delete/', views.MaturityHardDeleteView.as_view(), name="delete_maturity"),
    path('settings/electrofishers/', views.ElectrofisherFormsetView.as_view(), name="manage_electrofishers"),
    path('settings/electrofisher/<int:pk>/delete/', views.ElectrofisherHardDeleteView.as_view(), name="delete_electrofisher"),

    # SPECIES #
    ###########
    path('species/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),

    # RIVER #
    #########
    path('rivers/', views.RiverListView.as_view(), name="river_list"),
    path('rivers/new/', views.RiverCreateView.as_view(), name="river_new"),
    path('rivers/<int:pk>/view/', views.RiverDetailView.as_view(), name="river_detail"),
    path('rivers/<int:pk>/edit/', views.RiverUpdateView.as_view(), name="river_edit"),
    path('rivers/<int:pk>/delete/', views.RiverDeleteView.as_view(), name="river_delete"),

    # RIVER SITE #
    ##############
    path('rivers/<int:river>/new-site/', views.RiverSiteCreateView.as_view(), name="site_new"),
    path('sites/new/', views.RiverSiteCreateView.as_view(), name="site_new"),
    path('sites/<int:pk>/view/', views.RiverSiteDetailView.as_view(), name="site_detail"),
    path('sites/<int:pk>/edit/', views.RiverSiteUpdateView.as_view(), name="site_edit"),
    path('sites/<int:pk>/delete/', views.RiverSiteDeleteView.as_view(), name="site_delete"),

    # SAMPLE #
    ##########
    path('samples/', views.SampleListView.as_view(), name="sample_list"),
    path('samples/new/', views.SampleCreateView.as_view(), name="sample_new"),
    path('samples/<int:pk>/view/', views.SampleDetailView.as_view(), name="sample_detail"),
    path('samples/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="sample_edit"),
    path('samples/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="sample_delete"),

    # SWEEPS #
    ###############
    path('samples/<int:sample>/new-sweep/', views.SweepCreateView.as_view(), name='sweep_new'),
    path('sweeps/<int:pk>/view/', views.SweepDetailView.as_view(), name="sweep_detail"),
    path('sweeps/<int:pk>/edit/', views.SweepUpdateView.as_view(), name="sweep_edit"),
    path('sweeps/<int:pk>/delete/', views.SweepDeleteView.as_view(), name="sweep_delete"),

    # DATA ENTRY #
    ##############
    path('samples/<int:sample>/data-entry/', views.DataEntryVueJSView.as_view(), name="sample_data_entry"),
    path('sweeps/<int:sweep>/data-entry/', views.DataEntryVueJSView.as_view(), name="sweep_data_entry"),

    # OBSERVATION #
    ###############
    path('observations/', views.ObservationListView.as_view(), name="obs_list"),
    path('observations/<int:pk>/view/', views.ObservationDetailView.as_view(), name="obs_detail"),
    path('observations/<int:pk>/edit/', views.ObservationUpdateView.as_view(), name="obs_edit"),
    path('observations/<int:pk>/delete/', views.ObservationDeleteView.as_view(), name="obs_delete"),

    # FILES #
    #########
    path('observations/<int:obs>/new-file/', views.FileCreateView.as_view(), name='file_new'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

    # Reports #
    ###########
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),
    path('reports/samples/<str:year>/<str:sites>/', views.export_sample_data, name="sample_report"),
    path('reports/entries/<str:year>/<str:sites>/', views.export_entry_data, name="entry_report"),
    path('reports/opendata1/<str:year>/<str:sites>/', views.export_open_data_ver1, name="od1_report"),
    path('reports/opendata1/dictionary/', views.export_open_data_ver1_dictionary, name="od1_dictionary"),
    path('reports/opendata1/species-list/', views.export_spp_list, name="od_spp_list"),
    path('reports/opendata/wms/lang/<int:lang>/', views.export_open_data_ver1_wms, name="od1_wms"),

]

app_name = 'trapnet'
