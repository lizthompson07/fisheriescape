from django.urls import path

from . import views

urlpatterns = [
    # this should probably be moved to the shared models API, when created
    path("users/", views.UserListAPIView.as_view(), name="user-list"),

]
