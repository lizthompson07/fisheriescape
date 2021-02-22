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
    path('requests/<int:pk>/cancel/', views.TripRequestCancelUpdateView.as_view(), name="request_cancel"),
    path('requests/<int:pk>/submit/', views.TripRequestSubmitUpdateView.as_view(), name="request_submit"),
    path('requests/<int:pk>/edit/', views.TripRequestUpdateView.as_view(), name="request_edit"),
    path('requests/<int:pk>/delete/', views.TripRequestDeleteView.as_view(), name="request_delete"),
    path('requests/<int:pk>/clone/', views.TripRequestCloneUpdateView.as_view(), name="request_clone"),
    path('requests/<int:pk>/print-travel-plan/', views.TravelPlanPDF.as_view(), name="request_print"),
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
    path('request-reviewers/', views.TripRequestReviewerListView.as_view(), name="request_reviewer_list"),
    path('request-reviewers/<int:pk>/review/', views.TripRequestReviewerUpdateView.as_view(), name="request_reviewer_update"),



    ############################################################################################################

    # Trip reviewers
    ##################
    # path('review/<int:pk>/approve/for/<str:type>/', views.TripRequestReviewerUpdateView.as_view(), name="tr_review_update"),
    # path('adm-review/<int:pk>/<int:approve>/', views.TripRequestReviewerADMUpdateView.as_view(), name="tr_review_adm_update"),
    # path('trip/<int:trip>/reset-reviewers/from/<str:type>/', views.reset_trip_reviewers, name="reset_trip_reviewers"),
    # path('trip/<int:trip>/manage-reviewers/from/<str:type>/', views.manage_reviewers, name="manage_trip_reviewers"),
    # path('trip-reviewer/<int:pk>/delete/', views.TripReviewerHardDeleteView.as_view(), name="delete_trip_reviewer"),

    # REVIEWER APPROVAL
    path('trips-for-your-review/<str:which_ones>/', views.TripReviewListView.as_view(), name="trip_review_list"),
    # path('tagged-trips/', views.TripReviewListView.as_view(), name="trip_review_list"),
    # path('trip-reviewer/<int:pk>/review/', views.TripReviewerUpdateView.as_view(), name="trip_reviewer_update"),
    # path('trip/<int:pk>/skip/', views.SkipTripReviewerUpdateView.as_view(), name="trip_skip"),

    # TRIP #
    ########
    # path('trips/', views.TripListView.as_view(), name="trip_list"),
    # path('trips/<str:type>/', views.TripListView.as_view(), name="trip_list"),


    # verification / other admin views
    # path('trip/<int:pk>/admin-notes/', views.TripAdminNotesUpdateView.as_view(), name="trip_admin_notes_edit"),
    # path('trip/<int:pk>/review-process/', views.TripReviewProcessUpdateView.as_view(), name="trip_review_toggle"),
    # path('admin/trip-verification-list/region/<int:region>/adm/<int:adm>/', views.TripVerificationListView.as_view(),
    #      name="admin_trip_verification_list"),
    # path('trip/<int:pk>/verify/region/<int:region>/adm/<int:adm>/', views.TripVerifyUpdateView.as_view(), name="trip_verify"),
    # path('select-a-trip-to-reassign-requests-to/<int:pk>/', views.TripSelectFormView.as_view(), name="trip_reassign_select"),
    # path('re-assign-requests-from-trip/<int:trip_a>/to/<int:trip_b>/', views.TripReassignConfirmView.as_view(),
    #      name="trip_reassign_confirm"),

    # SETTINGS #
    ############
    path('settings/help-text/', views.HelpTextFormsetView.as_view(), name="manage_help_text"),
    path('settings/help-text/<int:pk>/delete/', views.HelpTextHardDeleteView.as_view(), name="delete_help_text"),
    path('settings/cost-categories/', views.CostCategoryFormsetView.as_view(), name="manage_cost_categories"),
    path('settings/cost-category/<int:pk>/delete/', views.CostCategoryHardDeleteView.as_view(), name="delete_cost_category"),
    path('settings/costs/', views.CostFormsetView.as_view(), name="manage_costs"),
    path('settings/cost/<int:pk>/delete/', views.CostHardDeleteView.as_view(), name="delete_cost"),
    path('settings/njc-rates/', views.NJCRatesFormsetView.as_view(), name="manage_njc_rates"),
    # path('settings/njc-rate/<int:pk>/delete/', views.NJCRatesHardDeleteView.as_view(), name="delete_njc_rate"),
    path('settings/trip-categories/', views.TripCategoryFormsetView.as_view(), name="manage_trip_categories"),
    # path('settings/trip-category/<int:pk>/delete/', views.TripCategoryHardDeleteView.as_view(), name="delete_trip_category"),
    path('settings/trip-subcategories/', views.TripSubcategoryFormsetView.as_view(), name="manage_trip_subcategories"),
    path('settings/trip-subcategory/<int:pk>/delete/', views.TripSubcategoryHardDeleteView.as_view(), name="delete_trip_subcategory"),
    # path('settings/trip-reasons/', views.ReasonFormsetView.as_view(), name="manage_reasons"),
    # path('settings/trip-reasons/<int:pk>/delete/', views.ReasonHardDeleteView.as_view(), name="delete_reason"),

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
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/export-cfts-list/year/<str:fy>/region/<str:region>/trip/<str:trip>/traveller/'
         '<str:user>/from_date/<str:from_date>/to_date/<str:to_date>/', views.export_cfts_list, name="export_cfts_list"),
    path('reports/cfts/request/<int:trip_request>/', views.export_request_cfts, name="export_cfts_request"),
    path('reports/cfts/trip/<int:trip>/', views.export_request_cfts, name="export_cfts_trip"),
    # path('event/<int:fy>/<str:email>/print/', views.TravelPlanPDF.as_view(), name="travel_plan"),

    path('reports/trip-list/fiscal-year/<str:fy>/region/<str:region>/adm/<str:adm>/from_date/<str:from_date>/to_date/<str:to_date>/',
         views.export_trip_list, name="export_trip_list"),
]
