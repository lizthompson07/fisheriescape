from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'inventory'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),

    # RESOURCE #
    ############
    path('', views.ResourceListView.as_view(), name ="resource_list" ),
    path('my-list/', views.MyResourceListView.as_view(), name ="my_resource_list" ),
    path('<int:pk>/view/', views.ResourceDetailView.as_view(), name ="resource_detail" ),
    path('<int:pk>/edit/', views.ResourceUpdateView.as_view(), name ="resource_edit" ),
    path('<int:pk>/delete/', views.ResourceDeleteView.as_view(), name ="resource_delete" ),
    path('new/', views.ResourceCreateView.as_view(), name ="resource_new" ),

    # RESOURCE PERSON #
    ###################
    path('<int:resource>/insert-person/', views.ResourcePersonFilterView.as_view(), name ="resource_person_filter" ),
    path('<int:resource>/person/<int:person>/add/', views.ResourcePersonCreateView.as_view(), name ="resource_person_add" ),
    path('resource-person/<int:pk>/delete/', views.ResourcePersonDeleteView.as_view(), name ="resource_person_delete" ),
    path('resource-person/<int:pk>/edit/', views.ResourcePersonUpdateView.as_view(), name ="resource_person_edit" ),


    # PEOPLE #
    ##########
    path('<int:resource>/insert-person/new/', views.PersonCreateView.as_view(), name ="person_add" ),
    path('<int:resource>/person/<int:person>/edit/', views.PersonUpdateView.as_view(), name ="person_edit" ),


    # RESOURCE KEYWORD #
    ####################
    path('<int:resource>/insert-keyword/', views.ResourceKeywordFilterView.as_view(), name ="resource_keyword_filter" ),
    path('<int:resource>/insert-topic-category/', views.ResourceTopicCategoryFilterView.as_view(), name ="resource_topic_category_filter" ),
    path('<int:resource>/insert-core-subject/', views.ResourceCoreSubjectFilterView.as_view(), name ="resource_core_subject_filter" ),
    path('<int:resource>/insert-species/', views.ResourceSpeciesFilterView.as_view(), name ="resource_species_filter" ),
    path('<int:resource>/insert-location/', views.ResourceLocationFilterView.as_view(), name ="resource_location_filter" ),
    path('<int:resource>/keyword/<int:keyword>/add-<slug:keyword_type>/', views.resource_keyword_add, name ="resource_keyword_add" ),
    path('<int:resource>/keyword/<int:keyword>/remove/', views.resource_keyword_delete, name ="resource_keyword_delete" ),
    # path('resource-keyword/<int:pk>/edit/', views.ResourceKeywordUpdateView.as_view(), name ="resource_keyword_edit" ),


    # KEYWORD #
    ###########
    path('<int:resource>/keyword/<int:pk>/view/', views.KeywordDetailView.as_view(), name ="keyword_detail" ),
    path('<int:resource>/keyword/<int:pk>/edit/', views.KeywordUpdateView.as_view(), name ="keyword_edit" ),
    path('<int:resource>/keyword/<int:keyword>/delete/', views.keyword_delete, name ="keyword_delete" ),
    path('<int:resource>/keyword/new/', views.KeywordCreateView.as_view(), name ="keyword_new" ),


    # RESOURCE CITATION #
    #####################
    path('<int:resource>/insert-citation/', views.ResourceCitationFilterView.as_view(), name ="resource_citation_filter" ),
    path('<int:resource>/citation/<int:citation>/add-citation/', views.resource_citation_add, name ="resource_citation_add" ),
    path('<int:resource>/citation/<int:citation>/remove/', views.resource_citation_delete, name ="resource_citation_delete" ),
    # path('resource-keyword/<int:pk>/edit/', views.ResourceKeywordUpdateView.as_view(), name ="resource_keyword_edit" ),

    # CITATION #
    ############
    path('<int:resource>/citation/<int:pk>/view/', views.CitationDetailView.as_view(), name ="citation_detail" ),
    path('<int:resource>/citation/<int:pk>/edit/', views.CitationUpdateView.as_view(), name ="citation_edit" ),
    path('<int:resource>/citation/<int:citation>/delete/', views.citation_delete, name ="citation_delete" ),
    path('<int:resource>/citation/new/', views.CitationCreateView.as_view(), name ="citation_new" ),

    # PUBLICATION #
    ###############
    path('publication/new/', views.PublicationCreateView.as_view(), name ="publication_new" ),

    # XML GOODNESS #
    ################
    path('<int:resource>/xml/export/publish-<slug:publish>/', views.export_resource_xml, name ="export_xml" ),
    path('<int:resource>/xml/export/', views.export_resource_xml, name ="export_xml" ),
    path('<int:resource>/xml/verify/', views.VerifyReadinessTemplateView.as_view(), name ="verify_readiness" ),

    # DATA MANAGEMENT ADMIN #
    #########################
    path('dm-admin/', views.DataManagementHomeTemplateView.as_view(), name ="dm_home" ),
    path('dm-admin/custodian-list/', views.DataManagementCustodianListView.as_view(), name ="dm_custodian_list" ),
    path('dm-admin/custodian/<int:pk>/detail/', views.DataManagementCustodianDetailView.as_view(), name ="dm_custodian_detail" ),
    path('dm-admin/custodian/<int:person>/send-request-for-certification/', views.send_certification_request, name ="send_certification_email" ),

    # RESOURCE CERTIFICATION #
    ##########################
    path('<int:resource>/certify/', views.ResourceCertificationCreateView.as_view(), name ="resource_certify" ),
    path('remove-certification/<int:pk>/', views.ResourceCertificationDeleteView.as_view(), name ="resource_certification_delete" ),
]
