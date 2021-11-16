from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'applications', views.ApplicationViewSet)
router.register(r'recommendations', views.RecommendationViewSet)
router.register(r'application-outcomes', views.ApplicationOutcomeViewSet)
router.register(r'achievements', views.AchievementViewSet)

urlpatterns = [
    path("res/", include(router.urls)),  # tested

    path("res/user/", views.CurrentUserAPIView.as_view(), name="res-current-user"),

    path("res/contexts/", views.ContextListAPIView.as_view(), name="res-context-list"),
    path("res/achievement-categories/", views.AchievementCategoryListAPIView.as_view(), name="res-achievement-category-list"),

    path("res/meta/models/application/", views.ApplicationModelMetaAPIView.as_view(), name="res-application-model-meta"),
    path("res/meta/models/recommendation/", views.RecommendationModelMetaAPIView.as_view(), name="res-recommendation-model-meta"),
    path("res/meta/models/achievement/", views.AchievementModelMetaAPIView.as_view(), name="res-achievement-model-meta"),

]
