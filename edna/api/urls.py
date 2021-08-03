from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'collections', views.CollectionViewSet)
router.register(r'filtration-batches', views.FiltrationBatchViewSet)
router.register(r'extraction-batches', views.ExtractionBatchViewSet)
router.register(r'samples', views.SampleViewSet)
router.register(r'filters', views.FilterViewSet)
router.register(r'extracts', views.DNAExtractViewSet)
router.register(r'pcrs', views.PCRViewSet)
router.register(r'pcr-assays', views.PCRAssayViewSet)
# router.register(r'observations', views.SpeciesObservationViewSet)

urlpatterns = [
    path("edna/", include(router.urls)),  # tested
    path("edna/user/", views.CurrentUserAPIView.as_view(), name="edna-current-user"),

    path("edna/meta/models/sample/", views.SampleModelMetaAPIView.as_view(), name="edna-sample-model-meta"),
    path("edna/meta/models/filter/", views.FilterModelMetaAPIView.as_view(), name="edna-filter-model-meta"),
    path("edna/meta/models/extract/", views.DNAExtractModelMetaAPIView.as_view(), name="edna-extract-model-meta"),
    path("edna/meta/models/pcr/", views.PCRModelMetaAPIView.as_view(), name="edna-pcr-model-meta"),
    path("edna/meta/models/pcr-assay/", views.PCRAssayModelMetaAPIView.as_view(), name="edna-pcr-assay-model-meta"),
    # path("edna/meta/models/species-observation/", views.SpeciesObservationModelMetaAPIView.as_view(), name="edna-pcr-model-meta"),

]
