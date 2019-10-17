from django.urls import path
from . import views

app_name = 'herring'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),
    # path('', views.IndexView.as_view(), name ="index" ),
    path('', views.index, name ="index" ),

    # SAMPLER #
    ###########
    path('sampler/new/', views.SamplerPopoutCreateView.as_view(), name ="sampler_new_pop"),
    path('sample/sampler/<int:sampler>/close/', views.SamplerCloseTemplateView.as_view(), name ="close_sampler" ),


    # SAMPLE #
    ##########
    path('samples/list/', views.SampleFilterView.as_view(), name ="sample_list"),
    path('samples/new/', views.SampleCreateView.as_view(), name ="sample_new"),
    path('samples/<int:pk>/detail/', views.SampleDetailView.as_view(), name ="sample_detail"),
    path('samples/<int:pk>/edit/', views.SampleUpdateView.as_view(), name ="sample_edit"),
    path('samples/<int:pk>/delete/', views.SampleDeleteView.as_view(), name ="sample_delete"),
    path('samples/<int:pk>/edit-fish-<str:type>/', views.SamplePopoutUpdateView.as_view(), name ="sample_edit_pop"),
    path('samples/go-to-next/from-sample/<int:sample>', views.move_sample_next, name ="move_sample_next"),

    # Length Frequency #
    ####################
    path('samples/<int:sample>/length-frequency-wizard-setup/', views.LengthFrquencyWizardSetupFormView.as_view(), name ="lf_wizard_setup"),
    path('samples/<int:sample>/length-frequency-wizard-confirmation/', views.LengthFrquencyWizardConfirmation.as_view(), name ="lf_wizard_confirmation"),
    path('samples/<int:sample>/from/<str:from_length>cm/to/<str:to_length>cm/on/<str:current_length>/', views.LengthFrquencyWizardFormView.as_view(), name ="lf_wizard"),
    path('samples/<int:sample>/length-frequency-correction-at-<str:current_length>cm/<int:pk>/', views.LengthFrquencyUpdateView.as_view(), name ="lf_wizard_correction"),

    # FISH DETAIL #
    ##############
    path('samples/<int:sample>/fish/<int:pk>/view/', views.FishDetailView.as_view(), name ="fish_detail"),
    path('samples/<int:sample>/fish/new/', views.FishCreateView.as_view(), name ="fish_create"),
    path('samples/<int:sample>/fish/<int:pk>/edit/', views.FishUpdateView.as_view(), name ="fish_update"),
    path('samples/<int:sample>/fish/<int:pk>/delete/', views.FishDeleteView.as_view(), name ="fish_delete"),
    # Lab
    path('samples/<int:sample>/lab-sample-confirmation', views.LabSampleConfirmation.as_view(), name ="lab_sample_confirmation"),
    path('samples/<int:sample>/new-lab-sample', views.lab_sample_primer, name ="lab_sample_primer"),
    path('samples/<int:sample>/lab/fish/<int:pk>/', views.LabSampleUpdateView.as_view(), name ="lab_sample_form"),
    path('samples/<int:sample>/fish-board-test/', views.FishboardTestView.as_view(), name ="fishboard_test_form"),
    path('samples/<int:sample>/delete/<int:pk>/', views.delete_fish_detail, name ="delete_fish_detail"),

    # Otolith
    path('samples/<int:sample>/otolith/fish/<int:pk>/', views.OtolithUpdateView.as_view(), name ="otolith_form"),
    # path('samples/<int:sample>/otolith/fish/<int:pk>/', views.OtolithUpdateView.as_view(), name ="otolith_form"),

    # SHARED #
    ##########
    path('sample/<int:sample>/<str:type>/<str:direction>/<int:current_id>/', views.move_record, name ="move_record" ),
    path('sample/<int:sample>/<str:type>/<str:direction>/', views.move_record, name ="move_record" ),

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
