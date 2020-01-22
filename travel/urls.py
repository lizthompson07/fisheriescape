from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # TRIP REQUEST #
    ################
    path('trips/', views.TripListView.as_view(), name="trip_list"),
    path('trip/new/', views.TripCreateView.as_view(), name="trip_new"),
    path('trip/<int:pk>/view/', views.TripDetailView.as_view(), name="trip_detail"),
    path('trip/<int:pk>/print/', views.TravelPlanPDF.as_view(), name="trip_print"),
    path('trip/<int:pk>/edit/', views.TripUpdateView.as_view(), name="trip_edit"),
    path('trip/<int:pk>/edit/<str:pop>/', views.TripUpdateView.as_view(), name="trip_edit"),
    path('trip/<int:pk>/delete/', views.TripDeleteView.as_view(), name="trip_delete"),
    path('trip/<int:pk>/delete/pop/<str:pop>/', views.TripDeleteView.as_view(), name="trip_delete"),
    path('trip/<int:pk>/duplicate/', views.TripCloneUpdateView.as_view(), name="duplicate_event"),
    path('trip/<int:pk>/new-child-trip/', views.TripCreateView.as_view(), name="trip_new"),
    path('trip/<int:pk>/clone-duplicate/pop/<str:pop>', views.ChildTripCloneUpdateView.as_view(), name="child_duplicate_event"),
    path('trip/<int:pk>/submit/', views.TripSubmitUpdateView.as_view(), name="trip_submit"),
    path('trip/<int:pk>/re-add-reviewers/', views.reset_reviewers, name="reset_reviewers"),

    # REVIEWER APPROVAL
    path('trips/review/', views.TripReviewListView.as_view(), name="trip_review_list"),
    path('trips/review/<str:which_ones>/', views.TripReviewListView.as_view(), name="trip_review_list"),
    path('review/<int:pk>/approve/', views.ReviewerApproveUpdateView.as_view(), name="review_approve"),
    path('review/<int:pk>/skip/', views.SkipReviewerUpdateView.as_view(), name="reviewer_skip"),

    # ADMIN APPROVAL
    path('admin/approval/', views.TripAdminApprovalListView.as_view(), name="admin_approval_list"),
    # path('admin/<int:pk>/approve/', views.TripAdminApproveUpdateView.as_view(), name="admin_approve"),

    # REVIEWERS #
    #############
    path('trip/<int:trip>/manage-reviewers/', views.manage_reviewers, name="manage_reviewers"),
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
    path('trip/<int:trip>/file/new/', views.FileCreateView.as_view(), name='file_new'),
    path('file/<int:pk>/view/', views.FileDetailView.as_view(), name='file_detail'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/export-cfts-list/year/<int:fy>/user/<int:user>/', views.export_cfts_list, name="export_cfts_list"),
    path('reports/cfts/trip/<int:pk>/', views.export_trip_cfts, name="export_cfts"),
    # path('event/<int:fy>/<str:email>/print/', views.TravelPlanPDF.as_view(), name="travel_plan"),


    # SETTINGS #
    ############
    path('settings/statuses/', views.manage_statuses, name="manage_statuses"),
    path('settings/status/<int:pk>/delete/', views.delete_status, name="delete_status"),
    path('settings/help-text/', views.manage_help_text, name="manage_help_text"),
    path('settings/help-text/<int:pk>/delete/', views.delete_help_text, name="delete_help_text"),

]
