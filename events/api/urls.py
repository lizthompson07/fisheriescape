from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'notes', views.NoteViewSet)
router.register(r'invitees', views.InviteeViewSet)

urlpatterns = [
    # this should probably be moved to the shared models API, when created
    path("users/", views.UserListAPIView.as_view(), name="user-list"),


    path("events-planner/meta/models/event/", views.EventModelMetaAPIView.as_view(), name="event-model-meta"),
    path("events-planner/meta/models/note/", views.NoteModelMetaAPIView.as_view(), name="note-model-meta"),
    path("events-planner/meta/models/invitee/", views.InviteeModelMetaAPIView.as_view(), name="invitee-model-meta"),
    path("events-planner/", include(router.urls)),

]
