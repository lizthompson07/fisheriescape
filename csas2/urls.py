from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # requests
    path('requests/', views.CSASRequestListView.as_view(), name="request_list"),
    path('requests/new/', views.CSASRequestCreateView.as_view(), name="request_new"),
    path('requests/<int:pk>/view/', views.CSASRequestDetailView.as_view(), name="request_detail"),
    path('requests/<int:pk>/edit/', views.CSASRequestUpdateView.as_view(), name="request_edit"),
    path('requests/<int:pk>/delete/', views.CSASRequestDeleteView.as_view(), name="request_delete"),
    path('requests/<int:pk>/submit/', views.CSASRequestSubmitView.as_view(), name="request_submit"),

    # request reviews
    path('requests/<int:crequest>/new-review/', views.CSASRequestReviewCreateView.as_view(), name="review_new"),
    path('reviews/<int:pk>/edit/', views.CSASRequestReviewUpdateView.as_view(), name="review_edit"),
    path('reviews/<int:pk>/delete/', views.CSASRequestReviewDeleteView.as_view(), name="review_delete"),

    # request files
    path('requests/<int:crequest>/new-file/', views.CSASRequestFileCreateView.as_view(), name='request_file_new'),
    path('files/<int:pk>/edit/', views.CSASRequestFileUpdateView.as_view(), name='request_file_edit'),
    path('files/<int:pk>/delete/', views.CSASRequestFileDeleteView.as_view(), name='request_file_delete'),

    # processes
    path('processes/', views.ProcessListView.as_view(), name="process_list"),
    path('processes/new/', views.ProcessCreateView.as_view(), name="process_new"),
    path('processes/<int:pk>/view/', views.ProcessDetailView.as_view(), name="process_detail"),
    path('processes/<int:pk>/edit/', views.ProcessUpdateView.as_view(), name="process_edit"),
    path('processes/<int:pk>/delete/', views.ProcessDeleteView.as_view(), name="process_delete"),

    # meetings
    path('processes/<int:pk>/new-meeting/', views.MeetingCreateView.as_view(), name="meeting_new"),
    path('meetings/<int:pk>/view/', views.MeetingDetailView.as_view(), name="meeting_detail"),
    path('meetings/<int:pk>/edit/', views.MeetingUpdateView.as_view(), name="meeting_edit"),
    path('meetings/<int:pk>/delete/', views.MeetingDeleteView.as_view(), name="meeting_delete"),

    # reports
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),  # tested

]

app_name = 'csas2'
