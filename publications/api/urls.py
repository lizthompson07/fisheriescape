from django.urls import path

from . import views

urlpatterns = [
    path("publications/user/", views.CurrentPublicationUserAPIView.as_view(), name="current-publication-user"),  # tested

    path("publications/pubs/", views.PublicationsAPIView.as_view(), name="api-pubs"),  # tested
]
