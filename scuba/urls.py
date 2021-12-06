from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # reference tables
    path('settings/divers/', views.DiverFormsetView.as_view(), name="manage_divers"),  # tested
    path('settings/diver/<int:pk>/delete/', views.DiverHardDeleteView.as_view(), name="delete_diver"),  # tested
    path('settings/species/', views.SpeciesFormsetView.as_view(), name="manage_species"),
    path('settings/species/<int:pk>/delete/', views.SpeciesHardDeleteView.as_view(), name="delete_species"),

    # user permissions
    path('settings/users/', views.ScubaUserFormsetView.as_view(), name="manage_scuba_users"),
    path('settings/users/<int:pk>/delete/', views.ScubaUserHardDeleteView.as_view(), name="delete_scuba_user"),

    # regions
    path('regions/', views.RegionListView.as_view(), name="region_list"),  # tested
    path('regions/new/', views.RegionCreateView.as_view(), name="region_new"),  # tested
    path('regions/<int:pk>/edit/', views.RegionUpdateView.as_view(), name="region_edit"),  # tested
    path('regions/<int:pk>/delete/', views.RegionDeleteView.as_view(), name="region_delete"),  # tested
    path('regions/<int:pk>/view/', views.RegionDetailView.as_view(), name="region_detail"),  # tested

    # sites
    # path('regions/<int:region>/new-site/', views.SiteCreateView.as_view(), name="site_new"),  # tested
    # path('sites/<int:pk>/edit/', views.SiteUpdateView.as_view(), name="site_edit"),  # tested
    # path('sites/<int:pk>/delete/', views.SiteDeleteView.as_view(), name="site_delete"),  # tested
    # path('sites/<int:pk>/view/', views.SiteDetailView.as_view(), name="site_detail"),  # tested

    # transects
    path('regions/<int:region>/new-transect/', views.TransectCreateView.as_view(), name="transect_new"),  # tested
    path('transects/<int:pk>/edit/', views.TransectUpdateView.as_view(), name="transect_edit"),  # tested
    path('transects/<int:pk>/delete/', views.TransectDeleteView.as_view(), name="transect_delete"),  # tested

    # samples
    path('samples/', views.SampleListView.as_view(), name="sample_list"),  # tested
    path('samples/new/', views.SampleCreateView.as_view(), name="sample_new"),  # tested
    path('samples/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="sample_edit"),  # tested
    path('samples/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="sample_delete"),  # tested
    path('samples/<int:pk>/view/', views.SampleDetailView.as_view(), name="sample_detail"),  # tested

    # dives
    path('samples/<int:sample>/new-dive/', views.DiveCreateView.as_view(), name="dive_new"),  # tested
    path('dives/<int:pk>/edit/', views.DiveUpdateView.as_view(), name="dive_edit"),  # tested
    path('dives/<int:pk>/delete/', views.DiveDeleteView.as_view(), name="dive_delete"),  # tested
    path('dives/<int:pk>/view/', views.DiveDetailView.as_view(), name="dive_detail"),  # tested
    path('dives/<int:pk>/data-entry/', views.DiveDataEntryDetailView.as_view(), name="dive_data_entry"),  # tested

    # reports
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),  # tested
    path('reports/dive-log/', views.dive_log_report, name="dive_log_report"),  # tested
    path('reports/transects/', views.export_transect_data, name="export_transect_data"),  # TODO: TESTME
    path('reports/dive/', views.export_dive_data, name="export_dive_data"),  # TODO: TESTME
    path('reports/section/', views.export_section_data, name="export_section_data"),  # TODO: TESTME
    path('reports/observations/', views.export_obs_data, name="export_obs_data"),  # TODO: TESTME

]

app_name = 'scuba'
