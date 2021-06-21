from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'observations', views.ObservationViewSet)

urlpatterns = [
    path("trapnet/user/", views.CurrentUserAPIView.as_view(), name="trapnet-current-user"),
    path("trapnet/", include(router.urls)),
    # path("trapnet/meta/models/observation/", views.ObservationModelMetaAPIView.as_view(), name="trapnet-observation-model-meta"),
    # path("trapnet/meta/models/species/", views.SpeciesModelMetaAPIView.as_view(), name="trapnet-species-model-meta"),

]
