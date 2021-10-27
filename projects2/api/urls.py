from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'project-years', views.ProjectYearViewSet)
router.register(r'staff', views.StaffViewSet)
router.register(r'om-costs', views.OMCostViewSet)
router.register(r'capital-costs', views.CapitalCostViewSet)
router.register(r'activities', views.ActivityViewSet)
router.register(r'collaboration', views.CollaborationViewSet)
router.register(r'status-reports', views.StatusReportViewSet)
router.register(r'activity-updates', views.ActivityUpdateViewSet)
router.register(r'citations', views.CitationViewSet)
router.register(r'reviews', views.ReviewViewSet)

urlpatterns = [
    path("ppt/", include(router.urls)),  # tested

    # functional api views
    path("ppt/user/", views.CurrentUserAPIView.as_view(), name="projects2-current-user"),  # tested
    path("ppt/fte-breakdown/", views.FTEBreakdownAPIView.as_view(), name="projects2-fte-breakdown"),  # tested
    path("ppt/financials/", views.FinancialsAPIView.as_view(), name="projects2-financials"),

    # lookups
    path("ppt/fiscal-years/", views.FiscalYearListAPIView.as_view(), name="projects2-fiscal-year-list"),
    path("ppt/tags/", views.TagListAPIView.as_view(), name="projects2-tag-list"),
    path("ppt/themes/", views.ThemeListAPIView.as_view(), name="projects2-theme-list"),
    path("ppt/functional-groups/", views.FunctionalGroupListAPIView.as_view(), name="projects2-group-list"),
    path("ppt/funding-sources/", views.FundingSourceListAPIView.as_view(), name="projects2-funding-source-list"),
    path("ppt/regions/", views.RegionListAPIView.as_view(), name="projects2-region-list"),
    path("ppt/divisions/", views.DivisionListAPIView.as_view(), name="projects2-division-list"),
    path("ppt/sections/", views.SectionListAPIView.as_view(), name="projects2-section-list"),
    path("ppt/publications/", views.PublicationListAPIView.as_view(), name="projects2-publication-list"),

    # model lookups
    path("ppt/meta/models/activity/", views.ActivityModelMetaAPIView.as_view(), name="projects-activity-model-meta"),
    path("ppt/meta/models/om-cost/", views.OMCostModelMetaAPIView.as_view(), name="projects-omcost-model-meta"),

]
