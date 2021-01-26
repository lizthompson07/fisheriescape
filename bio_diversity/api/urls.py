from django.urls import path

from . import views

urlpatterns = [
    path("bio_diversity/user/", views.CurrentUserAPIView.as_view(), name="current-user"),  # tested


]
