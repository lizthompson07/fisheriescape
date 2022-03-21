from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import ScoreViewSet

router = DefaultRouter()

router.register(r"scores", ScoreViewSet)
# router.register(r"profiles", ScoreListView)

urlpatterns = [
    path("fisheriescape/", include((router.urls, 'fisheriescape'), namespace='test')),
    # path("avatar/", ScoreListView.as_view(), name="score-looky")
]
