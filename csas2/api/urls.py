from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'requests', views.CSASRequestViewSet)
router.register(r'request-notes', views.CSASRequestNoteViewSet)
router.register(r'request-reviews', views.CSASRequestReviewViewSet)
router.register(r'processes', views.ProcessViewSet)
router.register(r'process-notes', views.ProcessNoteViewSet)
router.register(r'process-costs', views.ProcessCostViewSet)
router.register(r'meetings', views.MeetingViewSet)
router.register(r'meeting-notes', views.MeetingNoteViewSet)
router.register(r'invitees', views.InviteeViewSet)
router.register(r'resources', views.MeetingResourceViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'authors', views.AuthorViewSet)
router.register(r'document-notes', views.DocumentNoteViewSet)
router.register(r'doc-tracking', views.DocumentTrackingViewSet)
router.register(r'people', views.PersonViewSet)


urlpatterns = [
    path("csas/", include(router.urls)),  # tested
    path("csas/user/", views.CurrentUserAPIView.as_view(), name="csas-current-user"),

    path("csas/meta/models/request/", views.RequestModelMetaAPIView.as_view(), name="csas-request-review-model-meta"),
    path("csas/meta/models/request-review/", views.RequestReviewModelMetaAPIView.as_view(), name="csas-request-review-model-meta"),
    path("csas/meta/models/cost/", views.GenericCostModelMetaAPIView.as_view(), name="csas-cost-model-meta"),
    path("csas/meta/models/note/", views.GenericNoteModelMetaAPIView.as_view(), name="note-model-meta"),

    path("csas/meta/models/meeting/", views.MeetingModelMetaAPIView.as_view(), name="event-model-meta"),
    path("csas/meta/models/invitee/", views.InviteeModelMetaAPIView.as_view(), name="invitee-model-meta"),
    path("csas/meta/models/person/", views.PersonModelMetaAPIView.as_view(), name="person-model-meta"),
    path("csas/meta/models/resource/", views.ResourceModelMetaAPIView.as_view(), name="resource-model-meta"),
    path("csas/invitees/<int:pk>/invitation/", views.InviteeSendInvitationAPIView.as_view(), name="invitee-send-invitation"),

    path("csas/meta/models/document/", views.DocumentModelMetaAPIView.as_view(), name="csas-doc-model-meta"),
    path("csas/meta/models/document-tracking/", views.DocumentTrackingModelMetaAPIView.as_view(), name="csas-doc-tracking-model-meta"),
    path("csas/meta/models/author/", views.AuthorModelMetaAPIView.as_view(), name="csas-author-model-meta"),
    path("csas/meta/models/process/", views.ProcessModelMetaAPIView.as_view(), name="csas-process-model-meta"),
]
