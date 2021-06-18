from django.urls import path

from .views import biofouling_views, shared_views, ir_views, gc_views

app_name = 'grais'

urlpatterns = [

    # SETTINGS
    path('', shared_views.IndexView.as_view(), name="index"),  # tested

    path('settings/probes/', shared_views.ProbeFormsetView.as_view(), name="manage_probes"),  # tested
    path('settings/probe/<int:pk>/delete/', shared_views.ProbeHardDeleteView.as_view(), name="delete_probe"),  # tested
    path('settings/samplers/', shared_views.SamplerFormsetView.as_view(), name="manage_samplers"),  # tested
    path('settings/sampler/<int:pk>/delete/', shared_views.SamplerHardDeleteView.as_view(), name="delete_sampler"),  # tested
    path('settings/weather-conditions/', shared_views.WeatherConditionFormsetView.as_view(), name="manage_weather_conditions"),  # tested
    path('settings/weather-condition/<int:pk>/delete/', shared_views.WeatherConditionHardDeleteView.as_view(), name="delete_weather_condition"),  # tested
    path('settings/baits/', gc_views.BaitFormsetView.as_view(), name="manage_baits"),
    path('settings/bait/<int:pk>/delete/', gc_views.BaitHardDeleteView.as_view(), name="delete_bait"),

    # species
    path('species/', shared_views.SpeciesListView.as_view(), name="species_list"),  # tested
    path('species/new/', shared_views.SpeciesCreateView.as_view(), name="species_new"),  # tested
    path('species/<int:pk>/edit/', shared_views.SpeciesUpdateView.as_view(), name="species_edit"),  # tested
    path('species/<int:pk>/delete/', shared_views.SpeciesDeleteView.as_view(), name="species_delete"),  # tested
    path('species/<int:pk>/view/', shared_views.SpeciesDetailView.as_view(), name="species_detail"),  # tested

    # station #
    ###########
    path('stations/', biofouling_views.StationListView.as_view(), name="station_list"),  # tested
    path('stations/new/', biofouling_views.StationCreateView.as_view(), name="station_new"),  # tested
    path('stations/<int:pk>/view/', biofouling_views.StationDetailView.as_view(), name="station_detail"),  # tested
    path('stations/<int:pk>/edit/', biofouling_views.StationUpdateView.as_view(), name="station_edit"),  # tested
    path('stations/<int:pk>/delete/', biofouling_views.StationDeleteView.as_view(), name="station_delete"),  # tested

    # sample #
    ##########
    path('samples/', biofouling_views.SampleListView.as_view(), name="sample_list"),  # tested
    path('samples/new/', biofouling_views.SampleCreateView.as_view(), name="sample_new"),  # tested
    path('samples/<int:pk>/view/', biofouling_views.SampleDetailView.as_view(), name="sample_detail"),  # tested
    path('samples/<int:pk>/edit/', biofouling_views.SampleUpdateView.as_view(), name="sample_edit"),  # tested
    path('samples/<int:pk>/delete/', biofouling_views.SampleDeleteView.as_view(), name="sample_delete"),  # tested

    # sample note #
    ###############
    path('samples/<int:sample>/new-note/', biofouling_views.SampleNoteCreateView.as_view(), name="sample_note_new"),  # tested
    path('sample-notes/<int:pk>/edit/', biofouling_views.SampleNoteUpdateView.as_view(), name="sample_note_edit"),  # tested
    path('sample-notes/<int:pk>/delete/', biofouling_views.SampleNoteDeleteView.as_view(), name="sample_note_delete"),  # tested

    # probe measurements #
    ######################
    path('samples/<int:sample>/new-measurement/', biofouling_views.ProbeMeasurementCreateView.as_view(), name="measurement_new"),  # tested
    path('measurements/<int:pk>/edit/', biofouling_views.ProbeMeasurementUpdateView.as_view(), name="measurement_edit"),  # tested
    path('measurements/<int:pk>/delete/', biofouling_views.ProbeMeasurementDeleteView.as_view(), name="measurement_delete"),  # tested

    # species observations #
    ########################
    path('<str:type>/<int:pk>/observations/', biofouling_views.SpeciesObservationTemplateView.as_view(), name="species_observations"),  # tested

    # LINE #
    ########
    path('samples/<int:sample>/new-line/', biofouling_views.LineCreateView.as_view(), name="line_new"),  # tested
    path('lines/<int:pk>/view/', biofouling_views.LineDetailView.as_view(), name="line_detail"),  # tested
    path('lines/<int:pk>/edit/', biofouling_views.LineUpdateView.as_view(), name="line_edit"),  # tested
    path('lines/<int:pk>/delete/', biofouling_views.LineDeleteView.as_view(), name="line_delete"),  # tested

    # SURFACE #
    ###########
    path('lines/<int:line>/new-surface/', biofouling_views.SurfaceCreateView.as_view(), name="surface_new"),  # tested
    path('surfaces/<int:pk>/view/', biofouling_views.SurfaceDetailView.as_view(), name="surface_detail"),  # tested
    path('surfaces/<int:pk>/edit/', biofouling_views.SurfaceUpdateView.as_view(), name="surface_edit"),  # tested
    path('surfaces/<int:pk>/delete/', biofouling_views.SurfaceDeleteView.as_view(), name="surface_delete"),  # tested

    # INCIDENTAL REPORT #
    #####################
    path('incidental-reports/', ir_views.ReportListView.as_view(), name="ir_list"),  # tested
    path('incidental-reports/new/', ir_views.ReportCreateView.as_view(), name="ir_new"),  # tested
    path('incidental-reports/<int:pk>/view/', ir_views.ReportDetailView.as_view(), name="ir_detail"),  # tested
    path('incidental-reports/<int:pk>/edit/', ir_views.ReportUpdateView.as_view(), name="ir_edit"),  # tested
    path('incidental-reports/<int:pk>/delete/', ir_views.ReportDeleteView.as_view(), name="ir_delete"),  # tested

    # FOLLOWUP #
    ############
    path('incidental-reports/<int:report>/new-followup/', ir_views.FollowUpCreateView.as_view(), name="followup_new"),  # tested
    path('follow-up/<int:pk>/edit/', ir_views.FollowUpUpdateView.as_view(), name="followup_edit"),  # tested
    path('follow-up/<int:pk>/delete/', ir_views.FollowUpDeleteView.as_view(), name="followup_delete"),  # tested

    #
    # # ESTUARY #
    # ###########
    path('estuaries/', gc_views.EstuaryListView.as_view(), name="estuary_list"),  # tested
    path('estuaries/new/', gc_views.EstuaryCreateView.as_view(), name="estuary_new"),  # tested
    path('estuaries/<int:pk>/view/', gc_views.EstuaryDetailView.as_view(), name="estuary_detail"),  # tested
    path('estuaries/<int:pk>/edit/', gc_views.EstuaryUpdateView.as_view(), name="estuary_edit"),  # tested
    path('estuaries/<int:pk>/delete/', gc_views.EstuaryDeleteView.as_view(), name="estuary_delete"),  # tested

    # SITE #
    ###########
    path('estuaries/<int:estuary>/new-site/', gc_views.SiteCreateView.as_view(), name="site_new"),  # tested
    path('sites/<int:pk>/view/', gc_views.SiteDetailView.as_view(), name="site_detail"),  # tested
    path('sites/<int:pk>/edit/', gc_views.SiteUpdateView.as_view(), name="site_edit"),  # tested
    path('sites/<int:pk>/delete/', gc_views.SiteDeleteView.as_view(), name="site_delete"),  # tested

    # GC SAMPLE #
    #############
    path('green-crab-samples/', gc_views.GCSampleListView.as_view(), name="gcsample_list"),  # tested
    path('green-crab-samples/new/', gc_views.GCSampleCreateView.as_view(), name="gcsample_new"),  # tested
    path('green-crab-samples/<int:pk>/view/', gc_views.GCSampleDetailView.as_view(), name="gcsample_detail"),  # tested
    path('green-crab-samples/<int:pk>/edit/', gc_views.GCSampleUpdateView.as_view(), name="gcsample_edit"),  # tested
    path('green-crab-samples/<int:pk>/delete/', gc_views.GCSampleDeleteView.as_view(), name="gcsample_delete"),  # tested

    # probe measurements #
    ######################
    path('green-crab-samples/<int:sample>/new-measurement/', gc_views.GCProbeMeasurementCreateView.as_view(), name="gcmeasurement_new"),  # tested
    path('green-crab-measurements/<int:pk>/edit/', gc_views.GCProbeMeasurementUpdateView.as_view(), name="gcmeasurement_edit"),  # tested
    path('green-crab-measurements/<int:pk>/delete/', gc_views.GCProbeMeasurementDeleteView.as_view(), name="gcmeasurement_delete"),  # tested

    # TRAP #
    ########
    path('green-crab-samples/<int:sample>/new-trap/', gc_views.TrapCreateView.as_view(), name="trap_new"),  # tested
    path('traps/<int:pk>/view/', gc_views.TrapDetailView.as_view(), name="trap_detail"),  # tested
    path('traps/<int:pk>/edit/', gc_views.TrapUpdateView.as_view(), name="trap_edit"),  # tested
    path('traps/<int:pk>/delete/', gc_views.TrapDeleteView.as_view(), name="trap_delete"),  # tested

    # catch observations #
    ########################
    path('traps/<int:pk>/<str:type>-observations/', gc_views.CatchObservationTemplateView.as_view(), name="catch_observations"),  # tested

    # Reports #
    ###########
    path('reports/search/', shared_views.ReportSearchFormView.as_view(), name="reports"),  # tested
    path('reports/species-by-sample-spreadsheet/<str:species_list>/<str:year>/', shared_views.species_sample_spreadsheet_export, name="spp_sample_xlsx"),  # tested
    path('reports/biofouling-presence-absence/', shared_views.biofouling_presence_absence_spreadsheet_export, name="biofouling_pa_xlsx"),  # tested
    path('reports/opendata1/<int:year>/', shared_views.export_open_data_ver1, name="od1_report"),  # tested
    path('reports/opendata1/', shared_views.export_open_data_ver1, name="od1_report"),  # tested
    path('reports/opendata1/dictionary/', shared_views.export_open_data_ver1_dictionary, name="od1_dictionary"),  # tested
    path('reports/opendata1/wms/<str:year>/lang/<int:lang>/', shared_views.export_open_data_ver1_wms, name="od1_wms"),  # tested

    # GC monitoring
    path('reports/gc/<int:year>/cpue/', shared_views.export_gc_cpue, name="gc_cpue_report"),  # tested
    path('reports/gc/<int:year>/envr/', shared_views.export_gc_envr, name="gc_envr_report"),  # tested
    path('reports/gc/site-list/', shared_views.export_gc_sites, name="gc_site_report"),  # tested

]
