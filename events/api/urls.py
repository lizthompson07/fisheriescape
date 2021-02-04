from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'notes', views.NoteViewSet)

urlpatterns = [
    path("events-planner/meta/models/event/", views.EventModelMetaAPIView.as_view(), name="event-model-meta"),  # tested
    path("events-planner/meta/models/note/", views.NoteModelMetaAPIView.as_view(), name="note-model-meta"),  # tested

    path("events-planner/", include(router.urls)),

    # path("events/user/", views.CurrentUserAPIView.as_view(), name="current-events-user"),  # tested
    # path("events/user/", views.CurrentUserAPIView.as_view(), name="current-events-user"),  # tested


]
