from django.urls import path

from . import views

urlpatterns = [
    path("events/user/", views.CurrentUserAPIView.as_view(), name="current-events-user"),  # tested


]
