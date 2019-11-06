from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # SAR MAP #
    path('map/', views.SARMapTemplateView.as_view(), name="map"),
    path('map/n/<str:n>/s/<str:s>/e/<str:e>/w/<str:w>/', views.SARMapTemplateView.as_view(), name="map"),

    # SETTINGS #
    ############
    path('settings/taxa/', views.manage_taxa, name="manage_taxa"),
    path('settings/taxon/<int:pk>/delete/', views.delete_taxon, name="delete_taxon"),
    path('settings/statuses/', views.manage_statuses, name="manage_statuses"),
    path('settings/status/<int:pk>/delete/', views.delete_status, name="delete_status"),
    path('settings/schedules/', views.manage_schedules, name="manage_schedules"),
    path('settings/schedule/<int:pk>/delete/', views.delete_schedule, name="delete_schedule"),

    path('settings/CITES-appendices/', views.manage_appendices, name="manage_appendices"),
    path('settings/appendix/<int:pk>/delete/', views.delete_appendix, name="delete_appendix"),

    path('settings/authorities/', views.manage_authorities, name="manage_authorities"),
    path('settings/authority/<int:pk>/delete/', views.delete_authority, name="delete_authority"),

    # REGION #
    ###########
    path('regions/', views.RegionListView.as_view(), name="region_list"),
    path('region/new/', views.RegionCreateView.as_view(), name="region_new"),
    path('region/<int:pk>/view/', views.RegionDetailView.as_view(), name="region_detail"),
    path('region/<int:pk>/edit/', views.RegionUpdateView.as_view(), name="region_edit"),
    path('region/<int:pk>/delete/', views.RegionDeleteView.as_view(), name="region_delete"),
    path('region/<int:pk>/import-points-from-file/', views.RegionPolygonImportFileView.as_view(), name="region_polygon_file_import"),

    # REGION POLYGON #
    ##################
    # path('region/<int:region>/polygon/new/', views.RecordCreateView.as_view(), name="record_new"),
    path('region-polygon/<int:pk>/view/', views.RegionPolygonDetailView.as_view(), name="region_polygon_detail"),
    path('region-polygon/<int:pk>/edit/', views.RegionPolygonUpdateView.as_view(), name="region_polygon_edit"),
    path('region-polygon/<int:pk>/delete/', views.RegionPolygonDeleteView.as_view(), name="region_polygon_delete"),
    # points
    path('region-polygon/<int:region_polygon>/manage-coords/', views.manage_rp_coords, name="manage_rp_coords"),
    path('region-polygon-point/<int:pk>/delete/', views.delete_rp_coord, name="delete_rp_coord"),

    # SPECIES #
    ###########
    path('species/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),
    path('species/<int:pk>/import-points-from-file/', views.RecordImportFileView.as_view(), name="file_import"),

    # RECORD #
    ##########
    path('species/<int:species>/record/new/', views.RecordCreateView.as_view(), name="record_new"),
    # path('record/new/', views.RecordCreateView.as_view(), name="record_new"),
    path('record/<int:pk>/view/', views.RecordDetailView.as_view(), name="record_detail"),
    path('record/<int:pk>/edit/', views.RecordUpdateView.as_view(), name="record_edit"),
    path('record/<int:pk>/delete/', views.RecordDeleteView.as_view(), name="record_delete"),
    # points
    path('record/<int:record>/manage-coords/', views.manage_coords, name="manage_coords"),
    path('record-point/<int:pk>/delete/', views.delete_coord, name="delete_coord"),

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
