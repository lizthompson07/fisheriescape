from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'filters', views.FilterViewSet)  # tested

urlpatterns = [
    path("edna/", include(router.urls)),  # tested
    path("edna/user/", views.CurrentUserAPIView.as_view(), name="edna-current-user"),  # tested

    path("edna/meta/models/filter/", views.FilterModelMetaAPIView.as_view(), name="edna-filter-model-meta"),

]
