from django.urls import path

from . import views

urlpatterns = [
    path("publications/user/", views.CurrentPublicationUserAPIView.as_view(), name="current-publication-user"),

    path("publications/pubs/", views.PubsAPIView.as_view(), name="api-pubs"),  # not tested


]
