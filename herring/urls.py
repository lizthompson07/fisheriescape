from django.urls import path
from . import views

app_name = 'herring'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),
    path('', views.IndexView.as_view(), name ="index" ),

    # SAMPLER #
    ###########
    path('sampler/new/', views.SamplerPopoutCreateView.as_view(), name ="sampler_new_pop"),


    # PORT SAMPLE #
    ###############
    path('samples/list/', views.SampleFilterView.as_view(), name ="sample_list"),
    path('samples/port/new/', views.PortSampleCreateView.as_view(), name ="port_sample_new"),
    path('samples/port/<int:pk>/detail/', views.PortSampleDetailView.as_view(), name ="port_sample_detail"),
    path('samples/port/<int:pk>/edit/', views.PortSampleUpdateView.as_view(), name ="port_sample_edit"),
    path('samples/port/<int:pk>/delete/', views.PortSampleDeleteView.as_view(), name ="port_sample_delete"),
    path('samples/port/<int:pk>/edit-fish-<str:type>/', views.PortSamplePopoutUpdateView.as_view(), name ="port_sample_edit_pop"),


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
    # Otolith
    path('samples/<int:sample>/otolith/fish/<int:pk>/', views.OtolithUpdateView.as_view(), name ="otolith_form"),
    # path('samples/<int:sample>/otolith/fish/<int:pk>/', views.OtolithUpdateView.as_view(), name ="otolith_form"),

]
