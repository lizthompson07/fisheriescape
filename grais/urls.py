from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'grais'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexView.as_view(), name="index"),
    path('dataflow/', views.DataFlowTemplateView.as_view(), name="dataflow"),

    # SAMPLE #
    ##########
    path('sample/list/', views.SampleListView.as_view(), name="sample_list"),
    path('sample/new/', views.SampleCreateView.as_view(), name="sample_new"),
    path('sample/<int:pk>/view/', views.SampleDetailView.as_view(), name="sample_detail"),
    path('sample/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="sample_edit"),
    path('sample/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="sample_delete"),

    # STATION #
    ###########
    path('station/', views.StationListView.as_view(), name="station_list"),
    path('station/new/', views.StationCreateView.as_view(), name="station_create"),
    path('station/<int:pk>/view/', views.StationDetailView.as_view(), name="station_detail"),
    path('station/<int:pk>/edit/', views.StationUpdateView.as_view(), name="station_edit"),
    path('station/<int:pk>/delete/', views.StationDeleteView.as_view(), name="station_delete"),

    # SAMPLE NOTE #
    #############
    path('sample/<int:sample>/sample-note/new/', views.SampleNoteCreateView.as_view(), name="sample_note_new"),
    path('sample-note/<int:pk>/edit/', views.SampleNoteUpdateView.as_view(), name="sample_note_edit"),
    path('sample-note/<int:pk>/delete/', views.sample_note_delete, name="sample_note_delete"),

    # SPECIES #
    ###########
    path('species/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_create"),
    path('new-species-to-surface-<int:surface>/', views.SpeciesCreatePopoutView.as_view(), name="species_add"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),

    # PROBE MEASUREMENT #
    #####################
    path('sample/<int:sample>/probe-data/new/', views.ProbeMeasurementCreateView.as_view(),
         name="probe_measurement_new"),
    path('probe-data/<int:pk>/view/', views.ProbeMeasurementDetailView.as_view(), name="probe_measurement_detail"),
    path('probe-data/<int:pk>/edit/', views.ProbeMeasurementUpdateView.as_view(), name="probe_measurement_edit"),
    path('probe-data/<int:pk>/delete/', views.ProbeMeasurementDeleteView.as_view(), name="probe_measurement_delete"),

    # LINE #
    ########
    path('sample/<int:sample>/line/new/', views.LineCreateView.as_view(), name="line_new"),
    path('line/<int:pk>/view/', views.LineDetailView.as_view(), name="line_detail"),
    path('line/<int:pk>/edit/', views.LineUpdateView.as_view(), name="line_edit"),
    path('line/<int:pk>/delete/', views.LineDeleteView.as_view(), name="line_delete"),

    # SURFACE #
    ###########
    path('line/<int:line>/surface/new/', views.SurfaceCreateView.as_view(), name="surface_new"),
    path('surface/<int:pk>/view/', views.SurfaceDetailView.as_view(), name="surface_detail"),
    path('surface/<int:pk>/edit/', views.SurfaceUpdateView.as_view(), name="surface_edit"),
    path('surface/<int:pk>/delete/', views.SurfaceDeleteView.as_view(), name="surface_delete"),

    # SPECIES OBSERVATIONS (for sample + line level obs) #
    ########################################################
    path('species-observation/<str:type>/<int:pk>/insert/', views.SpeciesObservationInsertView.as_view(),
         name="spp_obs_insert"),
    path('species-observation/<str:type>/<int:pk>/new-spp/<int:species>/',
         views.SpeciesObservationCreatePopoutView.as_view(), name="spp_obs_new_pop"),
    path('species-observation/<str:type>/obs-pk/<int:pk>/edit/', views.SpeciesObservationUpdatePopoutView.as_view(),
         name="spp_obs_edit_pop"),
    # path('surface-species/<int:pk>/view/', views.SurfaceSpeciesDetailPopoutView.as_view(), name ="surface_spp_detail_pop" ),
    path('species-observation/<str:type>/obs-pk/<int:pk>/delete/return-to-<str:backto>/',
         views.species_observation_delete, name="spp_obs_delete"),

    # SURFACE SPECIES #
    ###################
    path('surface/<int:surface>/species/insert/', views.SurfacaeSpeciesInsertView.as_view(), name="surface_spp_insert"),
    path('surface/<int:surface>/species/<int:species>/new-surface-species/',
         views.SurfaceSpeciesCreatePopoutView.as_view(), name="surface_spp_new_pop"),
    path('surface-species/<int:pk>/edit/', views.SurfaceSpeciesUpdatePopoutView.as_view(), name="surface_spp_edit_pop"),
    # path('surface-species/<int:pk>/view/', views.SurfaceSpeciesDetailPopoutView.as_view(), name ="surface_spp_detail_pop" ),
    path('surface-species/<int:pk>/delete/return-to-<str:backto>/', views.surface_species_delete,
         name="surface_spp_delete"),

    path('person/new/', views.PersonCreateView.as_view(), name="person_create"),
    path('person/<int:pk>/view/', views.PersonDetailView.as_view(), name="person_detail"),
    path('person/<int:pk>/edit/', views.PersonUpdateView.as_view(), name="person_edit"),

    # INCIDENTAL REPORT #
    #####################
    path('incidental-report/list/', views.ReportListView.as_view(), name="report_list"),
    path('incidental-report/new/', views.ReportCreateView.as_view(), name="report_new"),
    path('incidental-report/<int:pk>/view/', views.ReportDetailView.as_view(), name="report_detail"),
    path('incidental-report/<int:pk>/edit/', views.ReportUpdateView.as_view(), name="report_edit"),
    path('incidental-report/<int:pk>/delete/', views.ReportDeleteView.as_view(), name="report_delete"),
    path('incidental-report/<int:report>/species/<int:species>/delete/', views.report_species_observation_delete,
         name="report_species_delete"),
    path('incidental-report/<int:report>/species/<int:species>/add/', views.report_species_observation_add, name="report_species_add"),

    # FOLLOWUP #
    ############
    path('report/<int:report>/follow-up/new/', views.FollowUpCreateView.as_view(), name="follow_up_new"),
    path('follow-up/<int:pk>/edit/', views.FollowUpUpdateView.as_view(), name="follow_up_edit"),
    path('follow-up/<int:pk>/delete/', views.follow_up_delete, name="follow_up_delete"),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/species-by-sample-spreadsheet/<str:species_list>/', views.species_sample_spreadsheet_export,
         name="spp_sample_xlsx"),

]
