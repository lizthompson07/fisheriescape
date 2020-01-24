from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # TRIP REQUEST #
    ################
    path('requests/', views.TripRequestListView.as_view(), name="request_list"),
    path('request/new/', views.TripRequestCreateView.as_view(), name="request_new"),
    path('request/<int:pk>/view/', views.TripRequestDetailView.as_view(), name="request_detail"),
    path('request/<int:pk>/print/', views.TravelPlanPDF.as_view(), name="request_print"),
    path('request/<int:pk>/edit/', views.TripRequestUpdateView.as_view(), name="request_edit"),
    path('request/<int:pk>/edit/<str:pop>/', views.TripRequestUpdateView.as_view(), name="request_edit"),
    path('request/<int:pk>/delete/', views.TripRequestDeleteView.as_view(), name="request_delete"),
    path('request/<int:pk>/delete/pop/<str:pop>/', views.TripRequestDeleteView.as_view(), name="request_delete"),
    path('request/<int:pk>/duplicate/', views.TripRequestCloneUpdateView.as_view(), name="duplicate_event"),
    path('request/<int:pk>/new-child-request/', views.TripRequestCreateView.as_view(), name="request_new"),
    path('request/<int:pk>/clone-duplicate/pop/<str:pop>', views.ChildTripRequestCloneUpdateView.as_view(), name="child_duplicate_event"),
    path('request/<int:pk>/submit/', views.TripRequestSubmitUpdateView.as_view(), name="request_submit"),
    path('request/<int:pk>/re-add-reviewers/', views.reset_reviewers, name="reset_reviewers"),

    # REVIEWER APPROVAL
    path('requests/review/', views.TripRequestReviewListView.as_view(), name="request_review_list"),
    path('requests/review/<str:which_ones>/', views.TripRequestReviewListView.as_view(), name="request_review_list"),
    path('review/<int:pk>/approve/', views.ReviewerApproveUpdateView.as_view(), name="review_approve"),
    path('review/<int:pk>/skip/', views.SkipReviewerUpdateView.as_view(), name="reviewer_skip"),

    # ADMIN APPROVAL
    path('admin/approval/', views.TripRequestAdminApprovalListView.as_view(), name="admin_approval_list"),
    # path('admin/<int:pk>/approve/', views.TripRequestAdminApproveUpdateView.as_view(), name="admin_approve"),

    # REVIEWERS #
    #############
    path('request/<int:trip_request>/manage-reviewers/', views.manage_reviewers, name="manage_reviewers"),
    path('reviewer/<int:pk>/delete/', views.delete_reviewer, name="delete_reviewer"),


    # CONFERENCE #
    ####################
    path('conferences/', views.ConferenceListView.as_view(), name="conf_list"),
    path('conference/new/', views.ConferenceCreateView.as_view(), name="conf_new"),
    path('conference/new/pop/<int:pop>/', views.ConferenceCreateView.as_view(), name="conf_new"),
    path('conference/<int:pk>/view/', views.ConferenceDetailView.as_view(), name="conf_detail"),
    path('conference/<int:pk>/edit/', views.ConferenceUpdateView.as_view(), name="conf_edit"),
    path('conference/<int:pk>/delete/', views.ConferenceDeleteView.as_view(), name="conf_delete"),

    # FILES #
    #########
    path('request/<int:trip_request>/file/new/', views.FileCreateView.as_view(), name='file_new'),
    path('file/<int:pk>/view/', views.FileDetailView.as_view(), name='file_detail'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/export-cfts-list/year/<int:fy>/user/<int:user>/', views.export_cfts_list, name="export_cfts_list"),
    path('reports/cfts/request/<int:pk>/', views.export_request_cfts, name="export_cfts"),
    # path('event/<int:fy>/<str:email>/print/', views.TravelPlanPDF.as_view(), name="travel_plan"),


    # SETTINGS #
    ############
    path('settings/statuses/', views.manage_statuses, name="manage_statuses"),
    path('settings/status/<int:pk>/delete/', views.delete_status, name="delete_status"),
    path('settings/help-text/', views.manage_help_text, name="manage_help_text"),
    path('settings/help-text/<int:pk>/delete/', views.delete_help_text, name="delete_help_text"),

]
