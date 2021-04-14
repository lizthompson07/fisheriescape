from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sample-species', views.SampleSpeciesViewSet)
router.register(r'line-species', views.LineSpeciesViewSet)
router.register(r'surface-species', views.SurfaceSpeciesViewSet)
router.register(r'incidental-report-species', views.IncidentalReportSpeciesViewSet)
router.register(r'catch-species', views.CatchViewSet)

urlpatterns = [
    path("grais/", include(router.urls)),  # tested
    path("grais/user/", views.CurrentUserAPIView.as_view(), name="grais-current-user"),


    path("grais/meta/models/species/", views.SpeciesModelMetaAPIView.as_view(), name="grais-species-model-meta"),
    path("grais/meta/models/catch/", views.CatchModelMetaAPIView.as_view(), name="grais-catch-model-meta"),

]
