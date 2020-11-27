from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
# router.register(r'project-years', views.ProjectYearViewSet)
urlpatterns = [
    # path("", include(router.urls)),
    path("project-planning/user/", views.CurrentUserAPIView.as_view(), name="current-user"),
    path("project-planning/fte-breakdown/", views.FTEBreakdownAPIView.as_view(), name="fte-breakdown"),

    # Project
    path("project-planning/projects/<int:pk>/", views.ProjectRetrieveAPIView.as_view(), name="year-detail"),
    path("project-planning/projects/", views.ProjectListAPIView.as_view(), name="project-list"),

    # Project year
    path("project-planning/project-years/", views.ProjectYearListAPIView.as_view(), name="year-list"),
    path("project-planning/project-years/<int:pk>/", views.ProjectYearRetrieveAPIView.as_view(), name="year-detail"),
    path("project-planning/project-years/<int:pk>/submit/", views.ProjectYearSubmitAPIView.as_view(), name="year-submit"),
    path("project-planning/project-years/<int:pk>/unsubmit/", views.ProjectYearUnsubmitAPIView.as_view(), name="year-unsubmit"),

    # Staff
    path("project-planning/project-years/<int:project_year>/staff/", views.StaffListCreateAPIView.as_view(), name="staff-list"),
    path("project-planning/staff/<int:pk>/", views.StaffRetrieveUpdateDestroyAPIView.as_view(), name="staff-detail"),
    path("project-planning/get-dates/", views.GetDatesAPIView.as_view(), name="get-dates"),

    # O&M
    path("project-planning/project-years/<int:project_year>/om-costs/", views.OMCostListCreateAPIView.as_view(), name="om-list"),
    path("project-planning/om-costs/<int:pk>/", views.OMCostRetrieveUpdateDestroyAPIView.as_view(), name="om-detail"),
    path("project-planning/project-years/<int:project_year>/add-all-costs/", views.AddAllCostsAPIView.as_view(), name="add-all-costs"),
    path("project-planning/project-years/<int:project_year>/remove-empty-costs/", views.RemoveEmptyCostsAPIView.as_view(), name="remove-empty-costs"),

    # Capital
    path("project-planning/project-years/<int:project_year>/capital-costs/", views.CapitalCostListCreateAPIView.as_view(), name="capital-list"),
    path("project-planning/capital-costs/<int:pk>/", views.CapitalCostRetrieveUpdateDestroyAPIView.as_view(), name="capital-detail"),

    # GC
    path("project-planning/project-years/<int:project_year>/gc-costs/", views.GCCostListCreateAPIView.as_view(), name="gc-list"),
    path("project-planning/gc-costs/<int:pk>/", views.GCCostRetrieveUpdateDestroyAPIView.as_view(), name="gc-detail"),

    # milestones
    path("project-planning/project-years/<int:project_year>/milestones/", views.MilestoneListCreateAPIView.as_view(), name="milestone-list"),
    path("project-planning/milestones/<int:pk>/", views.MilestoneRetrieveUpdateDestroyAPIView.as_view(), name="milestone-detail"),

    # collaborators
    path("project-planning/project-years/<int:project_year>/collaborators/", views.CollaboratorListCreateAPIView.as_view(), name="collaborator-list"),
    path("project-planning/collaborators/<int:pk>/", views.CollaboratorRetrieveUpdateDestroyAPIView.as_view(), name="collaborator-detail"),

    # agreements
    path("project-planning/project-years/<int:project_year>/agreements/", views.AgreementListCreateAPIView.as_view(), name="agreement-list"),
    path("project-planning/agreements/<int:pk>/", views.AgreementRetrieveUpdateDestroyAPIView.as_view(), name="agreement-detail"),

    # files
    path("project-planning/project-years/<int:project_year>/files/", views.FileListCreateAPIView.as_view(), name="file-list"),
    path("project-planning/files/<int:pk>/", views.FileRetrieveUpdateDestroyAPIView.as_view(), name="file-detail"),

    # financials
    path("project-planning/project-years/<int:project_year>/financials/", views.FinancialsAPIView.as_view(), name="financials"),
    path("project-planning/projects/<int:project>/financials/", views.FinancialsAPIView.as_view(), name="financials"),
    path("project-planning/financials/", views.FinancialsAPIView.as_view(), name="financials"),


    # lookups
    path("project-planning/fiscal-years/", views.FiscalYearListAPIView.as_view(), name="fiscal-year-list"),
    path("project-planning/tags/", views.TagListAPIView.as_view(), name="tag-list"),
    path("project-planning/themes/", views.ThemeListAPIView.as_view(), name="theme-list"),
    path("project-planning/functional-groups/", views.FunctionalGroupListAPIView.as_view(), name="group-list"),
    path("project-planning/funding-sources/", views.FundingSourceListAPIView.as_view(), name="funding-source-list"),
    path("project-planning/regions/", views.RegionListAPIView.as_view(), name="region-list"),
    path("project-planning/divisions/", views.DivisionListAPIView.as_view(), name="division-list"),
    path("project-planning/sections/", views.SectionListAPIView.as_view(), name="section-list"),

    # Reviews
    path("project-planning/project-years/<int:project_year>/reviews/", views.ReviewListCreateAPIView.as_view(), name="review-list"),
    path("project-planning/reviews/<int:pk>/", views.ReviewRetrieveUpdateDestroyAPIView.as_view(), name="review-detail"),

]

