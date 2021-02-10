from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'notes', views.NoteViewSet)
router.register(r'invitees', views.InviteeViewSet)
router.register(r'resources', views.ResourceViewSet)

urlpatterns = [
    path("events-planner/meta/models/event/", views.EventModelMetaAPIView.as_view(), name="event-model-meta"),
    path("events-planner/meta/models/note/", views.NoteModelMetaAPIView.as_view(), name="note-model-meta"),
    path("events-planner/meta/models/invitee/", views.InviteeModelMetaAPIView.as_view(), name="invitee-model-meta"),
    path("events-planner/meta/models/resource/", views.ResourceModelMetaAPIView.as_view(), name="resource-model-meta"),
    path("events-planner/", include(router.urls)),

    path("events-planner/invitees/<int:pk>/invitation/", views.InviteeSendInvitationAPIView.as_view(), name="invitee-send-invitation"),
]
