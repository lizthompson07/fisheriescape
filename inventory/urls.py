from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    # user permissions
    path('settings/users/', views.InventoryUserFormsetView.as_view(), name="manage_inventory_users"),
    path('settings/users/<int:pk>/delete/', views.InventoryUserHardDeleteView.as_view(), name="delete_inventory_user"),
    # role
    # org
    # storage solution
    # distribution format

    path('', views.Index.as_view(), name="index"),

    # RESOURCE #
    ############
    path('resources/', views.ResourceListView.as_view(), name="resource_list"),
    path('resources/new/', views.ResourceCreateView.as_view(), name="resource_new"),
    path('resources/<int:pk>/view/', views.ResourceDetailView.as_view(), name="resource_detail"),
    path('resources/<str:uuid>/', views.ResourceDetailView.as_view(), name="resource_detail_uuid"),
    path('resources/<int:pk>/pdf/', views.ResourceDetailPDFView.as_view(), name="resource_pdf"),
    path('resources/<int:pk>/edit/', views.ResourceUpdateView.as_view(), name="resource_edit"),
    path('resources/<int:pk>/clone/', views.ResourceCloneUpdateView.as_view(), name="resource_clone"),
    path('resources/<int:pk>/delete/', views.ResourceDeleteView.as_view(), name="resource_delete"),
    path('resources/<int:pk>/flag-for-deletion/', views.ResourceDeleteFlagUpdateView.as_view(), name="resource_flag_delete"),
    path('resources/<int:pk>/flag-for-publication/', views.ResourcePublicationFlagUpdateView.as_view(), name="resource_flag_publication"),
    path('resources/<int:pk>/add-to-favourites/', views.add_favourites, name="add_favourites"),
    path('resources/<int:pk>/remove-from-favourites/', views.remove_favourites, name="remove_favourites"),

    # Open Data
    path('open-data-dashboard/', views.OpenDataDashboardTemplateView.as_view(), name="open_data_dashboard"),

    # RESOURCE PERSON #
    ###################
    path('resources/<int:resource>/new-resource-person/', views.ResourcePersonCreateView.as_view(), name="resource_person_add"),
    path('resource-person/<int:pk>/delete/', views.ResourcePersonDeleteView.as_view(), name="resource_person_delete"),
    path('resource-person/<int:pk>/edit/', views.ResourcePersonUpdateView.as_view(), name="resource_person_edit"),


    # RESOURCE KEYWORD #
    ####################
    path('<int:pk>/insert-keyword/', views.ResourceKeywordUpdateView.as_view(), name="resource_keyword_edit"),
    path('<int:resource>/insert-keyword/', views.ResourceKeywordFilterView.as_view(), name="resource_keyword_filter"),
    path('<int:resource>/insert-topic-category/', views.ResourceTopicCategoryFilterView.as_view(), name="resource_topic_category_filter"),
    path('<int:resource>/insert-core-subject/', views.ResourceCoreSubjectFilterView.as_view(), name="resource_core_subject_filter"),
    path('<int:resource>/insert-species/', views.ResourceSpeciesFilterView.as_view(), name="resource_species_filter"),
    path('<int:resource>/insert-location/', views.ResourceLocationFilterView.as_view(), name="resource_location_filter"),
    path('<int:resource>/keyword/<int:keyword>/add-<slug:keyword_type>/', views.resource_keyword_add, name="resource_keyword_add"),
    path('<int:resource>/keyword/<int:keyword>/add/', views.resource_keyword_add, name="resource_keyword_add"),
    path('<int:resource>/keyword/<int:keyword>/remove/', views.resource_keyword_delete, name="resource_keyword_delete"),

    # KEYWORD #
    ###########
    path('<int:resource>/keyword/<int:pk>/view/', views.KeywordDetailView.as_view(), name="keyword_detail"),
    path('<int:resource>/keyword/<int:pk>/edit/', views.KeywordUpdateView.as_view(), name="keyword_edit"),
    path('<int:resource>/keyword/<int:keyword>/delete/', views.keyword_delete, name="keyword_delete"),
    path('<int:resource>/keyword/new/', views.KeywordCreateView.as_view(), name="keyword_new"),

    # RESOURCE CITATION #
    #####################
    path('<int:resource>/insert-citation/', views.ResourceCitationFilterView.as_view(), name="resource_citation_filter"),
    path('<int:resource>/citation/<int:citation>/add-citation/', views.resource_citation_add, name="resource_citation_add"),
    path('<int:resource>/citation/<int:citation>/remove/', views.resource_citation_delete, name="resource_citation_delete"),

    # CITATION #
    ############
    path('<int:resource>/citation/<int:pk>/view/', views.CitationDetailView.as_view(), name="citation_detail"),
    path('<int:resource>/citation/<int:pk>/edit/', views.CitationUpdateView.as_view(), name="citation_edit"),
    path('<int:resource>/citation/<int:citation>/delete/', views.citation_delete, name="citation_delete"),
    path('<int:resource>/citation/new/', views.CitationCreateView.as_view(), name="citation_new"),

    # PUBLICATION #
    ###############
    path('publication/new/', views.PublicationCreateView.as_view(), name="publication_new"),

    # XML GOODNESS #
    ################
    path('<int:resource>/xml/export/publish-<slug:publish>/', views.export_resource_xml, name="export_xml"),

    # DATA MANAGEMENT ADMIN #
    #########################
    path('dm-admin/custodian-list/', views.DataManagementCustodianListView.as_view(), name="dm_custodian_list"),
    path('dm-admin/custodian/<int:pk>/detail/', views.DataManagementCustodianDetailView.as_view(), name="dm_custodian_detail"),
    path('dm-admin/custodian/<int:person>/send-request-for-certification/', views.send_certification_request,
         name="send_certification_email"),
    path('dm-admin/custodian/<int:person>/', views.CustodianPersonUpdateView.as_view(), name="dm_person_edit"),

    # RESOURCE CERTIFICATION #
    ##########################
    path('resource/<int:resource>/certify/', views.ResourceCertificationCreateView.as_view(), name="resource_certify"),
    path('remove-certification/<int:pk>/', views.ResourceCertificationDeleteView.as_view(), name="resource_certification_delete"),

    # FILES #
    #########
    path('resource/<int:resource>/file/new/', views.FileCreateView.as_view(), name='file_create'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

    # DATA RESOURCE #
    #################
    path('resource/<int:resource>/data-resource/new/', views.DataResourceCreateView.as_view(), name='data_resource_create'),
    path('data-resource/<int:pk>/edit/', views.DataResourceUpdateView.as_view(), name='data_resource_edit'),
    path('data-resource/<int:pk>/delete/', views.DataResourceDeleteView.as_view(), name='data_resource_delete'),
    path('data-resource/<int:pk>/clone/', views.data_resource_clone, name='data_resource_clone'),

    # WEB SERVICES #
    #################
    path('resource/<int:resource>/web-service/new/', views.WebServiceCreateView.as_view(),
         name='web_service_create'),
    path('web-service/<int:pk>/edit/', views.WebServiceUpdateView.as_view(), name='web_service_edit'),
    path('web-service/<int:pk>/delete/', views.WebServiceDeleteView.as_view(), name='web_service_delete'),
    path('web-service/<int:pk>/clone/', views.web_service_clone, name='web_service_clone'),

    # DMAs #
    #################
    path('dmas/', views.DMAListView.as_view(), name="dma_list"),
    path('dmas/new/', views.DMACreateView.as_view(), name="dma_new"),
    path('dmas/<int:pk>/view/', views.DMADetailView.as_view(), name="dma_detail"),
    path('dmas/<int:pk>/edit/', views.DMAUpdateView.as_view(), name="dma_edit"),
    path('dmas/<int:pk>/delete/', views.DMADeleteView.as_view(), name="dma_delete"),
    path('dmas/<int:pk>/clone/', views.DMACloneView.as_view(), name="dma_clone"),

    # DMA Reviews #
    #################
    path('dmas/<int:dma>/new-review/', views.DMAReviewCreateView.as_view(), name="dma_review_new"),
    path('dma-reviews/<int:pk>/edit/', views.DMAReviewUpdateView.as_view(), name="dma_review_edit"),
    path('dmas-reviews/<int:pk>/delete/', views.DMAReviewDeleteView.as_view(), name="dma_review_delete"),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/export-batch-xml/<str:sections>/', views.export_batch_xml, name="export_batch_xml"),
    path('reports/odi-report/', views.export_odi_report, name="export_odi_report"),
    path('reports/physical-samples/', views.export_phyiscal_samples, name="export_phyiscal_samples"),
    path('reports/general-export/', views.export_resources, name="export_resources"),
    path('reports/open-data/', views.export_open_data_resources, name="export_open_data_resources"),
    path('reports/custodians/', views.export_custodians, name="export_custodians"),
    path('reports/dmas/', views.export_dmas, name="export_dmas"),

    # TEMP #
    ########

    #  this was used to walk over program to programs
    # path('metadata-formset/section/<int:section>/', views.temp_formset, name="formset"),
    # path('project-program-list/', views.MyTempListView.as_view(), name="my_list"),
    # path('reports/capacity-report/fy/<str:fy>/orgs/<str:orgs>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    # path('reports/capacity-report/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    # path('reports/capacity-report/fy/<str:fy>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    # path('reports/capacity-report/orgs/<str:orgs>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    # path('reports/cue-card/org/<int:org>/', views.OrganizationCueCard.as_view(), name="report_q"),

]
