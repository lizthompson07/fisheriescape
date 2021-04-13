from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # reports
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),  # tested

]

app_name = 'csas2'
