from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # reference tables
    path('settings/divers/', views.DiverFormsetView.as_view(), name="manage_divers"),  # tested
    path('settings/diver/<int:pk>/delete/', views.DiverHardDeleteView.as_view(), name="delete_diver"),  # tested

    # regions
    path('regions/', views.RegionListView.as_view(), name="region_list"),  # tested
    path('regions/new/', views.RegionCreateView.as_view(), name="region_new"),  # tested
    path('regions/<int:pk>/edit/', views.RegionUpdateView.as_view(), name="region_edit"),  # tested
    path('regions/<int:pk>/delete/', views.RegionDeleteView.as_view(), name="region_delete"),  # tested
    path('regions/<int:pk>/view/', views.RegionDetailView.as_view(), name="region_detail"),  # tested

    # sites
    path('regions/<int:region>/new-site/', views.SiteCreateView.as_view(), name="site_new"),  # tested
    path('sites/<int:pk>/edit/', views.SiteUpdateView.as_view(), name="site_edit"),  # tested
    path('sites/<int:pk>/delete/', views.SiteDeleteView.as_view(), name="site_delete"),  # tested
    path('sites/<int:pk>/view/', views.SiteDetailView.as_view(), name="site_detail"),  # tested

    # transects
    path('sites/<int:site>/new-transect/', views.TransectCreateView.as_view(), name="transect_new"),  # tested
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
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),# tested
    path('reports/dive-log/', views.dive_log_report, name="dive_log_report"),# tested

]

app_name = 'scuba'
