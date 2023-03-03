from django.urls import path
from rest_framework.routers import DefaultRouter

from fisheriescape.api import views


router = DefaultRouter()

app_name = "api"

urlpatterns = [

    path("fisheriescape/scores-feature/", views.ScoreFeatureView.as_view(), name="scores-feature"),
    path("fisheriescape/vulnerable-species-spots/", views.VulnerableSpeciesSpotsView.as_view(), name="vulnerable-species-spots"),
    # lookups
    path("fisheriescape/vulnerable-species/", views.VulnerableSpeciesView.as_view(), name="vulnerable-species"),
    path("fisheriescape/species/", views.SpeciesListAPIView.as_view(), name="fisheriescape-species-list"),
    path("fisheriescape/week/", views.WeekListAPIView.as_view(), name="fisheriescape-week-list"),
]
