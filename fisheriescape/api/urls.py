from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import ScoreViewSet, ScoreFeatureViewSet

router = DefaultRouter()

router.register(r"scores", ScoreViewSet)
router.register(r"scores-feature", ScoreFeatureViewSet, basename='scores-feature')
# router.register(r"profiles", ScoreListView)

urlpatterns = [
    path("fisheriescape/", include((router.urls, 'fisheriescape'), namespace='test')),
    # path("avatar/", ScoreListView.as_view(), name="score-looky")

    # lookups
    path("fisheriescape/species/", views.SpeciesListAPIView.as_view(), name="fisheriescape-species-list"),
    path("fisheriescape/week/", views.WeekListAPIView.as_view(), name="fisheriescape-week-list"),
]
