from django.urls import path
from . import views

app_name = 'herring'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),
    path('', views.IndexView.as_view(), name ="index" ),

    # PORT SAMPLE #
    ###############
    path('samples/list/', views.SampleFilterView.as_view(), name ="sample_list"),
    path('samples/port/new/', views.PortSampleCreateView.as_view(), name ="port_sample_new"),
    path('samples/port/<int:pk>/detail/', views.PortSampleDetailView.as_view(), name ="port_sample_detail"),
    path('samples/port/<int:pk>/edit/', views.PortSampleUpdateView.as_view(), name ="port_sample_edit"),
    path('samples/port/<int:pk>/delete/', views.PortSampleDeleteView.as_view(), name ="port_sample_delete"),

    # Length Frequency #
    ####################
    path('samples/<int:sample>/length-frequency-wizard-setup/', views.LengthFrquencyWizardSetupFormView.as_view(), name ="lf_wizard_setup"),
    path('samples/<int:sample>/length-frequency-wizard-confirmation/', views.LengthFrquencyWizardConfirmation.as_view(), name ="lf_wizard_confirmation"),
    path('samples/<int:sample>/from/<str:from_length>cm/to/<str:to_length>cm/on/<str:current_length>/', views.LengthFrquencyWizardFormView.as_view(), name ="lf_wizard"),
    path('samples/<int:sample>/length-frequency-correction-at-<str:current_length>cm/<int:pk>/', views.LengthFrquencyUpdateView.as_view(), name ="lf_wizard_correction"),

    # Fish Detail #
    ##############
    path('fish-detail/<int:pk>/view/', views.FishDetailView.as_view(), name ="fish_detail"),


]
