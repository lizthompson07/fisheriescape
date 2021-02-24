from django.urls import path

from . import views

app_name = 'travel'

urlpatterns = [
    # Download a file
    path('download/file/<str:file>/', views.get_file, name="get_file"),

    path('util/conf_details', views.get_conf_details, name='conf_details'),  # this should be moved to the API section
    path('', views.IndexTemplateView.as_view(), name="index"),

    # Requests
    ##########
    path('requests/', views.TripRequestListView.as_view(), name="request_list"),
    path('requests/new/', views.TripRequestCreateView.as_view(), name="request_new"),
    path('requests/<int:pk>/view/', views.TripRequestDetailView.as_view(), name="request_detail"),
    path('requests/view/<str:mystr>/<slug:uuid>/', views.TripRequestDetailView.as_view(), name="request_detail"), # for display in the TRAF
    path('requests/<int:pk>/cancel/', views.TripRequestCancelUpdateView.as_view(), name="request_cancel"),
    path('requests/<int:pk>/submit/', views.TripRequestSubmitUpdateView.as_view(), name="request_submit"),
    path('requests/<int:pk>/edit/', views.TripRequestUpdateView.as_view(), name="request_edit"),
    path('requests/<int:pk>/delete/', views.TripRequestDeleteView.as_view(), name="request_delete"),
    path('requests/<int:pk>/clone/', views.TripRequestCloneUpdateView.as_view(), name="request_clone"),
    path('requests/<int:pk>/TRAF/', views.TravelPlanPDF.as_view(), name="request_print"),
    path('requests/<int:pk>/reset-reviewers/', views.reset_request_reviewers, name="reset_request_reviewers"),

    # Trips
    #######
    path('trips/', views.TripListView.as_view(), name="trip_list"),
    path('trips/new/', views.TripCreateView.as_view(), name="trip_new"),

    path('trips/<int:pk>/view/', views.TripDetailView.as_view(), name="trip_detail"),
    path('trips/<int:pk>/edit/', views.TripUpdateView.as_view(), name="trip_edit"),
    path('trips/<int:pk>/clone/', views.TripCloneView.as_view(), name="trip_clone"),
    path('trips/<int:pk>/delete/', views.TripDeleteView.as_view(), name="trip_delete"),
    path('trips/<int:pk>/cancel/', views.TripCancelUpdateView.as_view(), name="trip_cancel"),

    path('trips/<int:pk>/verify/', views.TripVerifyUpdateView.as_view(), name="trip_verify"),
    path('trips/<int:pk>/review-process/', views.TripReviewProcessUpdateView.as_view(), name="trip_review_toggle"),

    # verification
    path('select-a-trip-to-reassign-requests-to/<int:pk>/', views.TripSelectFormView.as_view(), name="trip_reassign_select"),
    path('re-assign-requests-from-trip/<int:trip_a>/to/<int:trip_b>/', views.TripReassignConfirmView.as_view(),
         name="trip_reassign_confirm"),

    # Request reviews
    ##################
    path('request-reviewers/', views.RequestReviewerListView.as_view(), name="request_reviewer_list"),
    path('request-reviewers/<int:pk>/review/', views.RequestReviewerUpdateView.as_view(), name="request_reviewer_update"),

    # Trip reviews
    ##################
    path('trip-reviewers/', views.TripReviewerListView.as_view(), name="trip_reviewer_list"),
    path('trip-reviewers/<int:pk>/review/', views.TripReviewerUpdateView.as_view(), name="trip_reviewer_update"),


    ############################################################################################################


    # SETTINGS #
    ############
    path('settings/help-text/', views.HelpTextFormsetView.as_view(), name="manage_help_text"),
    path('settings/help-text/<int:pk>/delete/', views.HelpTextHardDeleteView.as_view(), name="delete_help_text"),
    path('settings/cost-categories/', views.CostCategoryFormsetView.as_view(), name="manage_cost_categories"),
    path('settings/cost-category/<int:pk>/delete/', views.CostCategoryHardDeleteView.as_view(), name="delete_cost_category"),
    path('settings/costs/', views.CostFormsetView.as_view(), name="manage_costs"),
    path('settings/cost/<int:pk>/delete/', views.CostHardDeleteView.as_view(), name="delete_cost"),
    path('settings/njc-rates/', views.NJCRatesFormsetView.as_view(), name="manage_njc_rates"),
    path('settings/trip-categories/', views.TripCategoryFormsetView.as_view(), name="manage_trip_categories"),
    path('settings/trip-subcategories/', views.TripSubcategoryFormsetView.as_view(), name="manage_trip_subcategories"),
    path('settings/trip-subcategory/<int:pk>/delete/', views.TripSubcategoryHardDeleteView.as_view(), name="delete_trip_subcategory"),

    path('settings/roles/', views.RoleFormsetView.as_view(), name="manage_roles"),
    path('settings/role/<int:pk>/delete/', views.RoleHardDeleteView.as_view(), name="delete_role"),

    path('settings/process-steps/', views.ProcessStepFormsetView.as_view(), name="manage_process_steps"),
    path('settings/process-step/<int:pk>/delete/', views.ProcessStepHardDeleteView.as_view(), name="delete_process_step"),

    path('settings/faqs/', views.FAQFormsetView.as_view(), name="manage_faqs"),
    path('settings/faq/<int:pk>/delete/', views.FAQHardDeleteView.as_view(), name="delete_faq"),

    path('settings/organizations/', views.OrganizationFormsetView.as_view(), name="manage_organizations"),
    path('settings/organization/<int:pk>/delete/', views.OrganizationHardDeleteView.as_view(), name="delete_organization"),

    # full
    path('settings/reference-materials/', views.ReferenceMaterialListView.as_view(), name="ref_mat_list"),
    path('settings/reference-materials/new/', views.ReferenceMaterialCreateView.as_view(), name="ref_mat_new"),
    path('settings/reference-materials/<int:pk>/edit/', views.ReferenceMaterialUpdateView.as_view(), name="ref_mat_edit"),
    path('settings/reference-materials/<int:pk>/delete/', views.ReferenceMaterialDeleteView.as_view(), name="ref_mat_delete"),

    # default reviewer settings
    path('default-reviewers/', views.DefaultReviewerListView.as_view(), name="default_reviewer_list"),
    path('default-reviewer/new/', views.DefaultReviewerCreateView.as_view(), name="default_reviewer_new"),
    path('default-reviewer/<int:pk>/edit/', views.DefaultReviewerUpdateView.as_view(), name="default_reviewer_edit"),
    path('default-reviewer/<int:pk>/delete/', views.DefaultReviewerDeleteView.as_view(), name="default_reviewer_delete"),

    # Admin Users
    path('settings/users/', views.UserListView.as_view(), name='user_list'),
    path('settings/users/travel/<int:travel>/', views.UserListView.as_view(), name='user_list'),
    path('settings/user/<int:pk>/toggle/<str:type>/', views.toggle_user, name='toggle_user'),

    # Reports #
    ###########
    path('reports/search/', views.ReportFormView.as_view(), name="reports"),
    path('reports/export-cfts-list/', views.export_cfts_list, name="export_cfts_list"),
    path('reports/trip-list/fiscal-year/', views.export_trip_list, name="export_trip_list"),

    path('reports/cfts/request/<int:trip_request>/', views.export_request_cfts, name="export_cfts_request"),
    path('reports/cfts/trip/<int:trip>/', views.export_request_cfts, name="export_cfts_trip"),
]
