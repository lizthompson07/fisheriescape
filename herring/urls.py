from django.urls import path

from . import views

app_name = 'herring'

urlpatterns = [
    # path('', views.IndexView.as_view(), name ="index" ),
    path('', views.IndexView.as_view(), name="index"),

    path('settings/users/', views.HerringUserFormsetView.as_view(), name="manage_herring_users"),  # tested
    path('settings/users/<int:pk>/delete/', views.HerringUserHardDeleteView.as_view(), name="delete_herring_user"),  # tested

    path('settings/samplers/', views.SamplerFormsetView.as_view(), name="manage_samplers"),  # tested
    path('settings/sampler/<int:pk>/delete/', views.SamplerHardDeleteView.as_view(), name="delete_sampler"),  # tested

    path('settings/gears/', views.GearFormsetView.as_view(), name="manage_gears"),  # tested
    path('settings/gear/<int:pk>/delete/', views.GearHardDeleteView.as_view(), name="delete_gear"),  # tested

    path('settings/fishing-areas/', views.FishingAreaFormsetView.as_view(), name="manage_fishing_areas"),  # tested
    path('settings/fishing-area/<int:pk>/delete/', views.FishingAreaHardDeleteView.as_view(), name="delete_fishing_area"),  # tested

    path('settings/mesh-sizes/', views.MeshSizeFormsetView.as_view(), name="manage_mesh_sizes"),  # tested
    path('settings/mesh-size/<int:pk>/delete/', views.MeshSizeHardDeleteView.as_view(), name="delete_mesh_size"),  # tested

    # species
    path('species/', views.SpeciesListView.as_view(), name="species_list"),  # tested
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),  # tested
    path('species/edit/<int:pk>/', views.SpeciesUpdateView.as_view(), name="species_edit"),  # tested
    path('species/delete/<int:pk>/', views.SpeciesDeleteView.as_view(), name="species_delete"),  # tested
    path('species/view/<int:pk>/', views.SpeciesDetailView.as_view(), name="species_detail"),  # tested

    # port
    path('ports/', views.PortListView.as_view(), name="port_list"),  # tested
    path('ports/new/', views.PortCreateView.as_view(), name="port_new"),  # tested
    path('ports/edit/<int:pk>/', views.PortUpdateView.as_view(), name="port_edit"),  # tested
    path('ports/delete/<int:pk>/', views.PortDeleteView.as_view(), name="port_delete"),  # tested
    path('ports/view/<int:pk>/', views.PortDetailView.as_view(), name="port_detail"),  # tested

    # SAMPLE #
    ##########
    path('samples/', views.SampleFilterView.as_view(), name="sample_list"),
    path('samples/search/', views.SampleSearchFormView.as_view(), name="sample_search"),
    path('samples/new/', views.SampleCreateView.as_view(), name="sample_new"),
    path('samples/<int:pk>/detail/', views.SampleDetailView.as_view(), name="sample_detail"),
    path('samples/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="sample_edit"),
    path('samples/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="sample_delete"),
    path('samples/go-to-next/from-sample/<int:sample>', views.move_sample_next, name="move_sample_next"),

    # Length Frequency #
    ####################
    path('samples/<int:sample>/length-frequencies/', views.LengthFrequencyDataEntryView.as_view(), name="lf"),

    # FISH DETAIL #
    ##############
    path('fish/<int:pk>/view/', views.FishDetailView.as_view(), name="fish_detail"),
    path('fish/<int:pk>/edit/', views.FishUpdateView.as_view(), name="fish_update"),
    path('fish/<int:pk>/delete/', views.FishDeleteView.as_view(), name="fish_delete"),

    # Lab
    path('lab/samples/<int:sample>/fish-board-test/', views.FishboardTestView.as_view(), name="fishboard_test_form"),
    path('lab/samples/<int:sample>/lab-sample-confirmation', views.LabSampleConfirmation.as_view(), name="lab_sample_confirmation"),
    path('lab/samples/<int:sample>/new-lab-sample', views.lab_sample_primer, name="lab_sample_primer"),
    path('lab/fish/<int:pk>/', views.LabSampleUpdateView.as_view(), name="lab_sample_form"),
    path('lab/fish/v2/<int:pk>/', views.LabSampleUpdateViewV2.as_view(), name="lab_sample_form_v2"),
    path('lab/delete/<int:pk>/', views.FishDetailHardDeleteView.as_view(), name="delete_fish_detail"),

    # Otolith
    path('otolith/fish/<int:pk>/', views.OtolithUpdateView.as_view(), name="otolith_form"),
    # path('samples/<int:sample>/otolith/fish/<int:pk>/', views.OtolithUpdateView.as_view(), name ="otolith_form"),

    # SHARED #
    ##########
    path('sample/<int:sample>/<str:type>/<str:direction>/<int:current_id>/', views.move_record, name="move_record"),
    path('sample/<int:sample>/<str:type>/<str:direction>/', views.move_record, name="move_record"),

    # PROGRESS REPORT #
    ###################
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('progress-report/<int:year>/', views.ProgressReportListView.as_view(), name="progress_report_detail"),
    path('progress-report/<int:year>/export/', views.export_progress_report, name="export_progress_report"),
    path('report/fish-detail/<int:year>/', views.export_fish_detail, name="export_fish_detail"),
    path('report/sample/<int:year>/', views.export_sample_report, name="export_sample_report"),
    path('hlen/<int:year>/export', views.export_hlen, name="export_hlen"),
    path('hlog/<int:year>/export', views.export_hlog, name="export_hlog"),
    path('hdet/<int:year>/export', views.export_hdet, name="export_hdet"),

    # IMPORTS #
    ###########
    path('import-from-csv/<str:type>/', views.ImportFileView.as_view(), name="import"),

    # ADMIN #
    #########
    path('check-usage/', views.CheckUsageListView.as_view(), name="check_usage"),

]
