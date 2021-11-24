from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
router = DefaultRouter()

router.register(r'regions', views.RegionViewSet)
router.register(r'sectors', views.SectorViewSet)
router.register(r'branches', views.BranchViewSet)
router.register(r'divisions', views.DivisionViewSet)
router.register(r'sections', views.SectionViewSet)

urlpatterns = [
    path("viewsets/", include(router.urls)),  # tested

    path("current-user/", views.CurrentUserAPIView.as_view(), name="current-user"),  # tested

    # this should probably be moved to the shared models API, when created
    path("users/", views.UserListAPIView.as_view(), name="user-list"),


    # lookups
    path("fiscal-years/", views.FiscalYearListAPIView.as_view(), name="fiscal-year-list"),
    path("regions/", views.RegionListAPIView.as_view(), name="region-list"),
    path("divisions/", views.DivisionListAPIView.as_view(), name="division-list"),
    path("sections/", views.SectionListAPIView.as_view(), name="section-list"),


]
