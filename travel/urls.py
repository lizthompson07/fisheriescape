from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),

    # EVENT #
    ##########
    path('events/', views.EventListView.as_view(), name="event_list"),
    path('event/new/', views.EventCreateView.as_view(), name="event_new"),
    path('event/<int:pk>/view/', views.EventDetailView.as_view(), name="event_detail"),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name="event_edit"),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name="event_delete"),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/export-cfts-list/<int:fy>/', views.export_cfts_list, name="export_cfts_list"),
    path('event/<int:fy>/<str:email>/print/', views.TravelPlanPDF.as_view(), name="travel_plan"),



]
