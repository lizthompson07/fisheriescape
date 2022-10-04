from django.urls import path, include

from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'committee', views.CommitteeViewSet)

urlpatterns = [
    path("maret/", include(router.urls))
]