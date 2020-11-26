from django.urls import path
from . import views

app_name = 'bio_diversity'

urlpatterns = [
    # for home/index page
    path('',                                        views.IndexTemplateView.as_view(),    name="index"),
    path('create/inst/', views.InstCreate.as_view(), name="create_inst")
    ]