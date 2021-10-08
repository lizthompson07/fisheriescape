from django.urls import path

from . import views

urlpatterns = [
    path("res/user/", views.CurrentUserAPIView.as_view(), name="res-current-user"),  # tested
]
