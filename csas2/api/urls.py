from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'filters', views.FilterViewSet)
router.register(r'extracts', views.DNAExtractViewSet)
router.register(r'pcrs', views.PCRViewSet)
router.register(r'observations', views.SpeciesObservationViewSet)

urlpatterns = [
    path("csas/", include(router.urls)),  # tested
    path("csas/user/", views.CurrentUserAPIView.as_view(), name="csas2-current-user"),

    path("csas/meta/models/filter/", views.FilterModelMetaAPIView.as_view(), name="csas2-filter-model-meta"),
    path("csas/meta/models/extract/", views.DNAExtractModelMetaAPIView.as_view(), name="csas2-extract-model-meta"),
    path("csas/meta/models/pcr/", views.PCRModelMetaAPIView.as_view(), name="csas2-pcr-model-meta"),
    path("csas/meta/models/species-observation/", views.SpeciesObservationModelMetaAPIView.as_view(), name="csas2-pcr-model-meta"),

]
