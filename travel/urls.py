from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # EVENT (TRIPS) #
    ##########
    path('trips/', views.EventListView.as_view(), name="event_list"),
    path('trip/new/', views.EventCreateView.as_view(), name="event_new"),
    path('trip/<int:pk>/view/', views.EventDetailView.as_view(), name="event_detail"),
    path('trip/<int:pk>/print/', views.TravelPlanPDF.as_view(), name="event_print"),
    path('trip/<int:pk>/edit/', views.EventUpdateView.as_view(), name="event_edit"),
    path('trip/<int:pk>/edit/<str:pop>/', views.EventUpdateView.as_view(), name="event_edit"),
    path('trip/<int:pk>/delete/', views.EventDeleteView.as_view(), name="event_delete"),
    path('trip/<int:pk>/delete/pop/<str:pop>/', views.EventDeleteView.as_view(), name="event_delete"),
    path('trip/<int:pk>/duplicate/', views.EventCloneUpdateView.as_view(), name="duplicate_event"),
    path('trip/<int:pk>/new-child-trip/', views.EventCreateView.as_view(), name="event_new"),

    path('trips/approval/', views.EventApprovalListView.as_view(), name="event_approval_list"),
    path('trips/approval/<str:which_ones>/', views.EventApprovalListView.as_view(), name="event_approval_list"),
    path('trip/<int:pk>/approve/', views.EventApproveUpdateView.as_view(), name="event_approve"),

    path('trip/<int:pk>/submit/', views.EventSubmitUpdateView.as_view(), name="event_submit"),

    path('admin/approval/', views.EventAdminApprovalListView.as_view(), name="admin_approval_list"),
    path('admin/<int:pk>/approve/', views.EventAdminApproveUpdateView.as_view(), name="admin_approve"),


    # REGISTERED EVENT #
    ####################
    path('events/', views.RegisteredEventListView.as_view(), name="revent_list"),
    path('event/new/', views.RegisteredEventCreateView.as_view(), name="revent_new"),
    path('event/new/pop/<int:pop>/', views.RegisteredEventCreateView.as_view(), name="revent_new"),
    path('event/<int:pk>/view/', views.RegisteredEventDetailView.as_view(), name="revent_detail"),
    path('event/<int:pk>/edit/', views.RegisteredEventUpdateView.as_view(), name="revent_edit"),
    path('event/<int:pk>/delete/', views.RegisteredEventDeleteView.as_view(), name="revent_delete"),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/export-cfts-list/year/<int:fy>/user/<int:user>/', views.export_cfts_list, name="export_cfts_list"),
    # path('event/<int:fy>/<str:email>/print/', views.TravelPlanPDF.as_view(), name="travel_plan"),

    # SETTINGS #
    ############
    path('settings/statuses/', views.manage_statuses, name="manage_statuses"),
    path('settings/status/<int:pk>/delete/', views.delete_status, name="delete_status"),

]
