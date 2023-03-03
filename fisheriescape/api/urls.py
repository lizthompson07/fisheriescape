from django.urls import path, include
from rest_framework.routers import DefaultRouter

from fisheriescape.api import views
from fisheriescape.api.views import ScoreFeatureView

router = DefaultRouter()

# router.register(r"scores", ScoreViewSet)
# router.register(r"scores-feature", ScoreFeatureViewSet, basename='scores-feature')
# router.register(r"profiles", ScoreListView)

app_name = "api"

urlpatterns = [
    # path("fisheriescape/", include((router.urls, 'fisheriescape'), namespace='api')),
    # path("avatar/", ScoreListView.as_view(), name="score-looky")

    path("fisheriescape/scores-feature/", views.ScoreFeatureView.as_view(), name="scores-feature"),
    # lookups
    path("fisheriescape/species/", views.SpeciesListAPIView.as_view(), name="fisheriescape-species-list"),
    path("fisheriescape/week/", views.WeekListAPIView.as_view(), name="fisheriescape-week-list"),
]
