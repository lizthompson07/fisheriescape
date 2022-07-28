from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

urlpatterns = [
    path("sar-search/", include(router.urls)),

    path("sar-search/user/", views.SarSeachCurrentUserAPIView.as_view(), name="sar-search-current-user"),

    path("sar-search/points/", views.PointsAPIView.as_view(), name="api-points"),
    path("sar-search/polygons/", views.PolygonsAPIView.as_view(), name="api-polygons"),
    path("sar-search/species/", views.SpeciesAPIView.as_view(), name="api-species"),

]
