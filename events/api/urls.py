from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
# router.register(r'hashtags', views.HashTagViewSet)

urlpatterns = [

    path("", include(router.urls)),

    # path("events/user/", views.CurrentUserAPIView.as_view(), name="current-events-user"),  # tested
    # path("events/user/", views.CurrentUserAPIView.as_view(), name="current-events-user"),  # tested


]
