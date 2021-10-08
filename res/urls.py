from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # # reference tables
    # path('settings/divers/', views.DiverFormsetView.as_view(), name="manage_divers"),  # tested
    # path('settings/diver/<int:pk>/delete/', views.DiverHardDeleteView.as_view(), name="delete_diver"),  # tested
    #
    #
    # # reports
    # path('reports/', views.ReportSearchFormView.as_view(), name="reports"),# tested
    # path('reports/dive-log/', views.dive_log_report, name="dive_log_report"),# tested

]

app_name = 'res'
