from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'applications', views.ApplicationViewSet)
router.register(r'recommendations', views.RecommendationViewSet)

urlpatterns = [
    path("res/", include(router.urls)),  # tested

    path("res/user/", views.CurrentUserAPIView.as_view(), name="res-current-user"),  # tested

    path("res/meta/models/application/", views.ApplicationModelMetaAPIView.as_view(), name="res-application-model-meta"),
    path("res/meta/models/recommendation/", views.RecommendationModelMetaAPIView.as_view(), name="res-recommendation-model-meta"),

]
