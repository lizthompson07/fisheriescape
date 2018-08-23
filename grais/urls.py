from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'grais'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),
    path('', views.IndexView.as_view(), name ="index" ),
    path('dataflow/', views.DataFlowTemplateView.as_view(), name ="dataflow" ),

    # SAMPLE #
    ##########
    path('sample/list', views.SampleListView.as_view(), name ="sample_list" ),
    path('sample/new', views.SampleCreateView.as_view(), name ="sample_new" ),
    path('sample/<int:pk>/view', views.SampleDetailView.as_view(), name ="sample_detail" ),
    path('sample/<int:pk>/edit', views.SampleUpdateView.as_view(), name ="sample_edit" ),
    path('sample/<int:pk>/delete', views.SampleDeleteView.as_view(), name ="sample_delete" ),

    # STATION #
    ###########
    path('station/', views.StationListView.as_view(), name ="station_list" ),
    path('station/new', views.StationCreateView.as_view(), name ="station_create" ),
    path('station/<int:pk>/view', views.StationDetailView.as_view(), name ="station_detail" ),
    path('station/<int:pk>/edit', views.StationUpdateView.as_view(), name ="station_edit" ),
    path('station/<int:pk>/delete', views.StationDeleteView.as_view(), name ="station_delete" ),

    # COLLECTOR #
    #############
    path('collector/', views.CollectorListView.as_view(), name ="collector_list" ),
    path('collector/new', views.CollectorCreateView.as_view(), name ="collector_create" ),
    path('collector/<int:pk>/view', views.CollectorDetailView.as_view(), name ="collector_detail" ),
    path('collector/<int:pk>/edit', views.CollectorUpdateView.as_view(), name ="collector_edit" ),
    path('collector/<int:pk>/delete', views.CollectorDeleteView.as_view(), name ="collector_delete" ),

    # SPECIES #
    ###########
    path('species/', views.SpeciesListView.as_view(), name ="species_list" ),
    path('species/new', views.SpeciesCreateView.as_view(), name ="species_create" ),
    path('new-species-to-surface-<int:surface>/', views.SpeciesCreatePopoutView.as_view(), name ="species_add" ),
    path('species/<int:pk>/view', views.SpeciesDetailView.as_view(), name ="species_detail" ),
    path('species/<int:pk>/edit', views.SpeciesUpdateView.as_view(), name ="species_edit" ),
    path('species/<int:pk>/delete', views.SpeciesDeleteView.as_view(), name ="species_delete" ),


    # PROBE MEASUREMENT #
    #####################
    path('sample/<int:sample>/probe-data/new/', views.ProbeMeasurementCreateView.as_view(), name ="probe_measurement_new" ),
    path('sample/<int:sample>/probe-data/<int:pk>/view/', views.ProbeMeasurementDetailView.as_view(), name ="probe_measurement_detail" ),
    path('sample/<int:sample>/probe-data/<int:pk>/edit/', views.ProbeMeasurementUpdateView.as_view(), name ="probe_measurement_edit" ),
    path('sample/<int:sample>/probe-data/<int:pk>/delete/', views.ProbeMeasurementDeleteView.as_view(), name ="probe_measurement_delete" ),

    # LINE #
    ########
    path('sample/<int:sample>/line/new/', views.LineCreateView.as_view(), name ="line_new" ),
    path('sample/<int:sample>/line/<int:pk>/view/', views.LineDetailView.as_view(), name ="line_detail" ),
    path('sample/<int:sample>/line/<int:pk>/edit/', views.LineUpdateView.as_view(), name ="line_edit" ),
    path('sample/<int:sample>/line/<int:pk>/delete/', views.LineDeleteView.as_view(), name ="line_delete" ),

    # SURFACE #
    ###########
    path('sample/<int:sample>/line/<int:line>/surface/new/', views.SurfaceCreateView.as_view(), name ="surface_new" ),
    path('sample/<int:sample>/line/<int:line>/surface/<int:pk>/view/', views.SurfaceDetailView.as_view(), name ="surface_detail" ),
    path('sample/<int:sample>/line/<int:line>/surface/<int:pk>/edit/', views.SurfaceUpdateView.as_view(), name ="surface_edit" ),
    path('sample/<int:sample>/line/<int:line>/surface/<int:pk>/delete/', views.SurfaceDeleteView.as_view(), name ="surface_delete" ),

    # SURFACE SPECIES #
    ###################
    path('sample/<int:sample>/line/<int:line>/surface/<int:surface>/species/insert/', views.SpeciesInsertListView.as_view() , name="surface_spp_insert"),
    path('sample/<int:sample>/line/<int:line>/surface/<int:surface>/species/<int:species>/new-surface=species/', views.SurfaceSpeciesCreatePopoutView.as_view(), name ="surface_spp_new_pop" ),
    path('sample/<int:sample>/line/<int:line>/surface/<int:surface>/surface-species/<int:pk>/edit/', views.SurfaceSpeciesUpdatePopoutView.as_view(), name ="surface_spp_edit_pop" ),
    path('sample/<int:sample>/line/<int:line>/surface/<int:surface>/surface-species/<int:pk>/view/', views.SurfaceSpeciesDetailPopoutView.as_view(), name ="surface_spp_detail_pop" ),
    path('sample/<int:sample>/line/<int:line>/surface/<int:surface>/surface-species/<int:pk>/delete/', views.SurfaceSpeciesDeletePopoutView.as_view(), name ="surface_spp_delete_pop" ),

    path('person/new', views.PersonCreateView.as_view(), name ="person_create" ),
    path('person/<int:pk>/view', views.PersonDetailView.as_view(), name ="person_detail" ),
    path('person/<int:pk>/edit', views.PersonUpdateView.as_view(), name ="person_edit" ),

    # CSV #
    #######
    path('csv-export/', views.export_csv_1, name ="export_csv_1" ),


]
