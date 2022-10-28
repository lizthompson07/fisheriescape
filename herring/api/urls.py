from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'length-frequencies', views.LengthFrequencyViewSet)
router.register(r'samples', views.SampleViewSet)

urlpatterns = [
    path("herman/", include(router.urls)),  # tested
    path("herman/user/", views.CurrentUserAPIView.as_view(), name="herman-current-user"),

]
