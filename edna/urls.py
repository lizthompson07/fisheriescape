from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # reference tables
    path('settings/filtration-types/', views.FiltrationTypeFormsetView.as_view(), name="manage_filtration_types"),  # tested
    path('settings/filtration-type/<int:pk>/delete/', views.FiltrationTypeHardDeleteView.as_view(), name="delete_filtration_type"),  # tested
    path('settings/dna-extraction-protocols/', views.DNAExtractionProtocolFormsetView.as_view(), name="manage_dna_extraction_protocols"),  # tested
    path('settings/dna-extraction-protocol/<int:pk>/delete/', views.DNAExtractionProtocolHardDeleteView.as_view(), name="delete_dna_extraction_protocol"),
    # tested
    path('settings/tags/', views.TagFormsetView.as_view(), name="manage_tags"),  # tested
    path('settings/tag/<int:pk>/delete/', views.TagHardDeleteView.as_view(), name="delete_tag"),  # tested

    path('settings/sample-types/', views.SampleTypeFormsetView.as_view(), name="manage_sample_types"),  # TODO: test
    path('settings/sample-type/<int:pk>/delete/', views.SampleTypeHardDeleteView.as_view(), name="delete_sample_type"),  # TODO: test

    path('settings/master-mixes/', views.MasterMixFormsetView.as_view(), name="manage_master_mixes"),
    path('settings/master-mix/<int:pk>/delete/', views.MasterMixHardDeleteView.as_view(), name="delete_master_mix"),


    # species
    path('species/', views.SpeciesListView.as_view(), name="species_list"),  # tested
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),  # tested
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),  # tested
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),  # tested
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),  # tested

    # assays
    path('assays/', views.AssayListView.as_view(), name="assay_list"),  # tested
    path('assays/new/', views.AssayCreateView.as_view(), name="assay_new"),  # tested
    path('assays/<int:pk>/edit/', views.AssayUpdateView.as_view(), name="assay_edit"),  # tested
    path('assays/<int:pk>/delete/', views.AssayDeleteView.as_view(), name="assay_delete"),  # tested
    path('assays/<int:pk>/view/', views.AssayDetailView.as_view(), name="assay_detail"),  # tested

    # collections
    path('collections/', views.CollectionListView.as_view(), name="collection_list"),  # tested
    path('collections/new/', views.CollectionCreateView.as_view(), name="collection_new"),  # tested
    path('collections/<int:pk>/edit/', views.CollectionUpdateView.as_view(), name="collection_edit"),  # tested
    path('collections/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name="collection_delete"),  # tested
    path('collections/<int:pk>/view/', views.CollectionDetailView.as_view(), name="collection_detail"),  # tested
    path('collections/<int:pk>/import-samples/', views.ImportSamplesView.as_view(), name="import_samples"),
    path('collections/<int:pk>/data-entry/', views.SampleDataEntryTemplateView.as_view(), name="sample_data_entry"),

    # files
    path('collections/<int:collection>/new-file/', views.FileCreateView.as_view(), name='file_new'),  # tested
    path('files/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),  # tested
    path('files/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),  # tested

    # samples
    path('collections/<int:collection>/new-sample/', views.SampleCreateView.as_view(), name="sample_new"),  # tested
    path('samples/<int:pk>/edit/', views.SampleUpdateView.as_view(), name="sample_edit"),  # tested
    path('samples/<int:pk>/delete/', views.SampleDeleteView.as_view(), name="sample_delete"),  # tested
    path('samples/<int:pk>/view/', views.SampleDetailView.as_view(), name="sample_detail"),  # tested
    path('samples/', views.SampleListView.as_view(), name="sample_list"),

    # filtration batches
    path('filtration-batches/', views.FiltrationBatchListView.as_view(), name="filtration_batch_list"),  # tested
    path('filtration-batches/new/', views.FiltrationBatchCreateView.as_view(), name="filtration_batch_new"),  # tested
    path('filtration-batches/<int:pk>/edit/', views.FiltrationBatchUpdateView.as_view(), name="filtration_batch_edit"),  # tested
    path('filtration-batches/<int:pk>/delete/', views.FiltrationBatchDeleteView.as_view(), name="filtration_batch_delete"),  # tested
    path('filtration-batches/<int:pk>/view/', views.FiltrationBatchDetailView.as_view(), name="filtration_batch_detail"),  # tested

    # extraction batches
    path('extraction-batches/', views.ExtractionBatchListView.as_view(), name="extraction_batch_list"),  # tested
    path('extraction-batches/new/', views.ExtractionBatchCreateView.as_view(), name="extraction_batch_new"),  # tested
    path('extraction-batches/<int:pk>/edit/', views.ExtractionBatchUpdateView.as_view(), name="extraction_batch_edit"),  # tested
    path('extraction-batches/<int:pk>/delete/', views.ExtractionBatchDeleteView.as_view(), name="extraction_batch_delete"),  # tested
    path('extraction-batches/<int:pk>/view/', views.ExtractionBatchDetailView.as_view(), name="extraction_batch_detail"),  # tested

    # pcr batches
    path('pcr-batches/', views.PCRBatchListView.as_view(), name="pcr_batch_list"),  # tested
    path('pcr-batches/new/', views.PCRBatchCreateView.as_view(), name="pcr_batch_new"),  # tested
    path('pcr-batches/<int:pk>/edit/', views.PCRBatchUpdateView.as_view(), name="pcr_batch_edit"),  # tested
    path('pcr-batches/<int:pk>/delete/', views.PCRBatchDeleteView.as_view(), name="pcr_batch_delete"),  # tested
    path('pcr-batches/<int:pk>/view/', views.PCRBatchDetailView.as_view(), name="pcr_batch_detail"),  # tested
    path('pcr-batches/import/', views.ImportPCRView.as_view(), name="import_pcrs"),

    # filters
    path('filters/', views.FilterListView.as_view(), name="filter_list"),
    path('filters/<int:pk>/view/', views.FilterDetailView.as_view(), name="filter_detail"),

    # extracts
    path('extracts/', views.DNAExtractListView.as_view(), name="extract_list"),
    path('extracts/<int:pk>/view/', views.DNAExtractDetailView.as_view(), name="extract_detail"),

    # pcrs
    path('pcrs/', views.PCRListView.as_view(), name="pcr_list"),
    path('pcrs/<int:pk>/view/', views.PCRDetailView.as_view(), name="pcr_detail"),

    # reports
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),  # tested

]

app_name = 'edna'
