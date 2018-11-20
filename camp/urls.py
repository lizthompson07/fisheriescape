from django.urls import path
from . import views
urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),
    path('', views.index, name ="index" ),
    path('search/', views.SearchFormView.as_view(), name ="sample_search" ),
    # path('dataflow/', views.DataFlowTemplateView.as_view(), name ="dataflow" ),

    # SAMPLE #
    ##########
    # path('samples/', views.SampleFilterView.as_view(), name ="sample_list" ),
    path('sample-list/year=<str:year>/month=<str:month>/site=<str:site>/stn=<str:station>/species=<str:species>/', views.SampleListView.as_view(), name ="sample_list" ),
    path('sample/new/', views.SampleCreateView.as_view(), name ="sample_new" ),
    path('sample/<int:pk>/view/', views.SampleDetailView.as_view(), name ="sample_detail" ),
    path('sample/<int:pk>/edit/', views.SampleUpdateView.as_view(), name ="sample_edit" ),
    path('sample/<int:pk>/delete/', views.SampleDeleteView.as_view(), name ="sample_delete" ),

    # SITE #
    ########
    path('sites/', views.SiteListView.as_view(), name ="site_list" ),
    path('site/new/', views.SiteCreateView.as_view(), name ="site_new" ),
    path('site/<int:pk>/view/', views.SiteDetailView.as_view(), name ="site_detail" ),
    path('site/<int:pk>/edit/', views.SiteUpdateView.as_view(), name ="site_edit" ),
    path('site/<int:pk>/delete/', views.SiteDeleteView.as_view(), name ="site_delete" ),

    # STATION #
    ###########
    path('site/<int:site>/new-station/', views.StationCreateView.as_view(), name ="station_new" ),
    path('new-station/', views.NoSiteStationCreateView.as_view(), name ="station_new" ),
    path('station/<int:pk>/view/', views.StationDetailView.as_view(), name ="station_detail" ),
    path('station/<int:pk>/edit/', views.StationUpdateView.as_view(), name ="station_edit" ),
    path('station/<int:pk>/delete/', views.StationDeleteView.as_view(), name ="station_delete" ),

    # SPECIES #
    ###########
    path('species/', views.SpeciesListView.as_view(), name ="species_list" ),
    path('species/new/', views.SpeciesCreateView.as_view(), name ="species_new" ),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name ="species_detail" ),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name ="species_edit" ),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name ="species_delete" ),


    # SPECIES OBSERVATIONS #
    ########################
    path('sample/<int:sample>/species/insert/', views.SpeciesObservationInsertView.as_view() , name="species_obs_search"),
    path('sample/<int:sample>/species/<int:species>/add/', views.SpeciesObservationCreateView.as_view(), name ="species_obs_new" ),
    path('species-observation/<int:pk>/edit/', views.SpeciesObservationUpdateView.as_view(), name ="species_obs_edit" ),
    path('species-observation/<int:pk>/delete/return-to-<str:backto>/', views.species_observation_delete, name ="species_obs_delete" ),
]

app_name = 'camp'

