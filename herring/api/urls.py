from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'length-frequencies', views.LengthFrequencyViewSet)
router.register(r'samples', views.SampleViewSet)
router.register(r'fish-details', views.FishDetailViewSet)
router.register(r'flags', views.FishDetailFlagViewSet)

urlpatterns = [
    path("herman/", include(router.urls)),  # tested
    path("herman/user/", views.CurrentUserAPIView.as_view(), name="herman-current-user"),
    path('herman/model-metas/', views.HerringModelMetadataAPIView.as_view(), name="herring-model-metas"),  # this should phase everything else out

]
