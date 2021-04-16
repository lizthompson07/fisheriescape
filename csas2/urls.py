from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    path('requests/', views.CSASRequestListView.as_view(), name="request_list"),
    path('requests/new/', views.CSASRequestCreateView.as_view(), name="request_new"),
    path('requests/<int:pk>/view/', views.CSASRequestDetailView.as_view(), name="request_detail"),
    path('requests/<int:pk>/edit/', views.CSASRequestUpdateView.as_view(), name="request_edit"),
    path('requests/<int:pk>/delete/', views.CSASRequestDeleteView.as_view(), name="request_delete"),

    # reports
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),  # tested

]

app_name = 'csas2'
