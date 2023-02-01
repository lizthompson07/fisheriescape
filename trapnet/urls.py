from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # SETTINGS #
    ############
    # user permissions
    path('settings/users/', views.TrapNetUserFormsetView.as_view(), name="manage_trap_net_users"),
    path('settings/users/<int:pk>/delete/', views.TrapNetUserHardDeleteView.as_view(), name="delete_trap_net_user"),

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
    path('settings/reproductive-statuses/', views.ReproductiveStatusFormsetView.as_view(), name="manage_reproductive_statuses"),
    path('settings/reproductive-statuses/<int:pk>/delete/', views.ReproductiveStatusHardDeleteView.as_view(), name="delete_reproductive_status"),

    path('settings/fishing-areas/', views.FishingAreaFormsetView.as_view(), name="manage_fishing_areas"),
    path('settings/fishing-area/<int:pk>/delete/', views.FishingAreaHardDeleteView.as_view(), name="delete_fishing_area"),

    path('settings/monitoring-programs/', views.MonitoringProgramFormsetView.as_view(), name="manage_monitoring_programs"),
    path('settings/monitoring-program/<int:pk>/delete/', views.MonitoringProgramHardDeleteView.as_view(), name="delete_monitoring_program"),

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
    path('samples/<int:pk>/review/', views.review_sample, name="review_sample"),

    # SAMPLE FILES #
    ################
    path('samples/<int:sample>/new-file/', views.SampleFileCreateView.as_view(), name='sample_file_new'),
    path('sample-files/<int:pk>/edit/', views.SampleFileUpdateView.as_view(), name='sample_file_edit'),
    path('sample-files/<int:pk>/delete/', views.SampleFileDeleteView.as_view(), name='sample_file_delete'),

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
    path('specimens/', views.SpecimenListView.as_view(), name="specimen_list"),
    path('specimens/<int:pk>/view/', views.SpecimenDetailView.as_view(), name="specimen_detail"),
    path('specimens/<int:pk>/edit/', views.SpecimenUpdateView.as_view(), name="specimen_edit"),
    path('specimens/<int:pk>/delete/', views.SpecimenDeleteView.as_view(), name="specimen_delete"),

    # FILES #
    #########
    path('specimens/<int:specimen>/new-file/', views.FileCreateView.as_view(), name='file_new'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

    # biological-detailing
    path('biological-detailings/', views.BiologicalDetailingListView.as_view(), name="biological_detailing_list"),  # tested
    # path('biological-detailings/edit/<int:pk>/', views.BiologicalDetailingUpdateView.as_view(), name="biological_detailing_edit"),  # tested
    # path('biological-detailings/delete/<int:pk>/', views.BiologicalDetailingDeleteView.as_view(), name="biological_detailing_delete"),  # tested
    path('biological-detailings/view/<int:pk>/', views.BiologicalDetailingDetailView.as_view(), name="biological_detailing_detail"),  # tested

    # Reports #
    ###########
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),
    path('reports/samples/', views.export_sample_data, name="sample_report"),
    path('reports/sweeps/', views.export_sweep_data, name="sweep_report"),
    path('reports/specimens/', views.export_specimen_data, name="specimen_report"),
    path('reports/river-sites/', views.river_site_report, name="river_site_report"),
    path('reports/specimens/v1/', views.export_specimen_data_v1, name="export_specimen_data_v1"),
    path('reports/biological-details/', views.export_biological_detailing_data, name="biological_detailing_report"),

    # od - summary by site
    path('reports/open-data/species-list/', views.od_sp_list, name="od_sp_list"),
    path('reports/open-data/summary-by-site-dictionary/', views.od_summary_by_site_dict, name="od_summary_by_site_dict"),
    path('reports/open-data/summary-by-site-report/', views.od_summary_by_site_report, name="od_summary_by_site_report"),
    path('reports/open-data/summary-by-site-wms/', views.od_summary_by_site_wms, name="od_summary_by_site_wms"),

    # electro
    path('reports/electrofishing/juv_salmon_report/', views.electro_juv_salmon_report, name="electro_juv_salmon_report"),

]

app_name = 'trapnet'
