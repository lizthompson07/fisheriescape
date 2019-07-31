from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # SETTINGS #
    ############
    path('settings/taxa/', views.manage_taxa, name="manage_taxa"),
    path('settings/taxon/<int:pk>/delete/', views.delete_taxon, name="delete_taxon"),
    path('settings/statuses/', views.manage_statuses, name="manage_statuses"),
    path('settings/status/<int:pk>/delete/', views.delete_status, name="delete_status"),
    path('settings/schedules/', views.manage_schedules, name="manage_schedules"),
    path('settings/schedule/<int:pk>/delete/', views.delete_schedule, name="delete_schedule"),
    path('settings/counties/', views.manage_counties, name="manage_counties"),
    path('settings/county/<int:pk>/delete/', views.delete_county, name="delete_county"),

    # SPECIES #
    ###########
    path('species/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),


    # RANGE #
    #########
    path('species/<int:species>/range/new/', views.RangeCreateView.as_view(), name="range_new"),
    # path('range/new/', views.RangeCreateView.as_view(), name="range_new"),
    path('range/<int:pk>/view/', views.RangeDetailView.as_view(), name="range_detail"),
    path('range/<int:pk>/edit/', views.RangeUpdateView.as_view(), name="range_edit"),
    path('range/<int:pk>/delete/', views.RangeDeleteView.as_view(), name="range_delete"),
    # points
    path('range/<int:range>/manage-coords/', views.manage_coords, name="manage_coords"),
    path('range-point/<int:pk>/delete/', views.delete_coord, name="delete_coord"),


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
