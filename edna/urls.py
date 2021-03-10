from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),
    #
    # # reference tables
    # path('settings/divers/', views.DiverFormsetView.as_view(), name="manage_divers"),  
    # path('settings/diver/<int:pk>/delete/', views.DiverHardDeleteView.as_view(), name="delete_diver"),  
    #
    # # regions
    # path('regions/', views.RegionListView.as_view(), name="region_list"),  
    # path('regions/new/', views.RegionCreateView.as_view(), name="region_new"),  
    # path('regions/<int:pk>/edit/', views.RegionUpdateView.as_view(), name="region_edit"),  
    # path('regions/<int:pk>/delete/', views.RegionDeleteView.as_view(), name="region_delete"),  
    # path('regions/<int:pk>/view/', views.RegionDetailView.as_view(), name="region_detail"),  
    #
    # # sites
    # path('regions/<int:region>/new-site/', views.SiteCreateView.as_view(), name="site_new"),  
    # path('sites/<int:pk>/edit/', views.SiteUpdateView.as_view(), name="site_edit"),  
    # path('sites/<int:pk>/delete/', views.SiteDeleteView.as_view(), name="site_delete"),  
    # path('sites/<int:pk>/view/', views.SiteDetailView.as_view(), name="site_detail"),  
    #
    # # transects
    # path('sites/<int:site>/new-transect/', views.TransectCreateView.as_view(), name="transect_new"),  
    # path('transects/<int:pk>/edit/', views.TransectUpdateView.as_view(), name="transect_edit"),  
    # path('transects/<int:pk>/delete/', views.TransectDeleteView.as_view(), name="transect_delete"),  
    #
    # # samples
    # path('samples/', views.SampleListView.as_view(), name="sample_list"),  
    # path('samples/new/', views.SampleCreateView.as_view(), name="sample_new"),  
    # path('samples/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="sample_edit"),  
    # path('samples/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="sample_delete"),  
    # path('samples/<int:pk>/view/', views.SampleDetailView.as_view(), name="sample_detail"),  
    #
    # # dives
    # path('samples/<int:sample>/new-dive/', views.DiveCreateView.as_view(), name="dive_new"),  
    # path('dives/<int:pk>/edit/', views.DiveUpdateView.as_view(), name="dive_edit"),  
    # path('dives/<int:pk>/delete/', views.DiveDeleteView.as_view(), name="dive_delete"),  
    # path('dives/<int:pk>/view/', views.DiveDetailView.as_view(), name="dive_detail"),  
    # path('dives/<int:pk>/data-entry/', views.DiveDataEntryDetailView.as_view(), name="dive_data_entry"),  
    #
    # # reports
    # path('reports/', views.ReportSearchFormView.as_view(), name="reports"),
    # path('reports/dive-log/', views.dive_log_report, name="dive_log_report"),

]

app_name = 'edna'
