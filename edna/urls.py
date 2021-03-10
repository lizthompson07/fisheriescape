from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # reference tables
    path('settings/experiment-types/', views.FiltrationTypeFormsetView.as_view(), name="manage_experiment_types"),
    path('settings/experiment-type/<int:pk>/delete/', views.FiltrationTypeHardDeleteView.as_view(), name="delete_experiment_type"),

    path('settings/dna-extraction-protocols/', views.DNAExtractionProtocolFormsetView.as_view(), name="manage_dna_extraction_protocols"),
    path('settings/dna-extraction-protocol/<int:pk>/delete/', views.DNAExtractionProtocolHardDeleteView.as_view(), name="delete_dna_extraction_protocol"),

    path('settings/tags/', views.TagFormsetView.as_view(), name="manage_tags"),
    path('settings/tag/<int:pk>/delete/', views.TagHardDeleteView.as_view(), name="delete_tag"),


    # species
    path('species/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),

    # collections
    path('collections/', views.CollectionListView.as_view(), name="collection_list"),
    path('collections/new/', views.CollectionCreateView.as_view(), name="collection_new"),
    path('collections/<int:pk>/edit/', views.CollectionUpdateView.as_view(), name="collection_edit"),
    path('collections/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name="collection_delete"),
    path('collections/<int:pk>/view/', views.CollectionDetailView.as_view(), name="collection_detail"),

    # samples
    path('collections/<int:collection>/new-sample/', views.SampleCreateView.as_view(), name="sample_new"),
    path('samples/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="sample_edit"),
    path('samples/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="sample_delete"),
    path('samples/<int:pk>/view/', views.SampleDetailView.as_view(), name="sample_detail"),
    path('samples/<int:pk>/data-entry/', views.SampleDataEntryDetailView.as_view(), name="sample_data_entry"),
    #
    # reports
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),

]

app_name = 'edna'
