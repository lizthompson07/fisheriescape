from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reservations', views.CSASRequestViewSet)


urlpatterns = [
    path("cars/", include(router.urls)),
]
