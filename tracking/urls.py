from django.conf.urls import url
from django.urls import path

from tracking import views

urlpatterns = [
    url(r'^$', views.dashboard, name='tracking-dashboard'),
    path('user/<int:user>/', views.user_history, name="user_history"),
    path('app/<str:app>/', views.app_history, name="app_history"),

    path('reports/users/', views.user_report, name="user_report"),
    path('reports/page_visit_summary_report/', views.page_visit_summary_report, name="page_visit_summary_report"),
    path('reports/user_summary_report/', views.user_summary_report, name="user_summary_report"),

]

app_name = "tracking"
