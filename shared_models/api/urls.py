from django.urls import path

from . import views

urlpatterns = [
    path("current-user/", views.CurrentUserAPIView.as_view(), name="current-user"),  # tested

    # this should probably be moved to the shared models API, when created
    path("users/", views.UserListAPIView.as_view(), name="user-list"),

]
