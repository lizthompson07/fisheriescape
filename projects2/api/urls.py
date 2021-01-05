from django.urls import path

from . import views

urlpatterns = [
    path("project-planning/user/", views.CurrentUserAPIView.as_view(), name="current-user"),  # tested
    path("project-planning/fte-breakdown/", views.FTEBreakdownAPIView.as_view(), name="fte-breakdown"),  # tested

    # Project
    path("project-planning/projects/<int:pk>/", views.ProjectRetrieveAPIView.as_view(), name="project-detail"),  # tested
    path("project-planning/projects/", views.ProjectListAPIView.as_view(), name="project-list"),  # tested

    # Project year
    path("project-planning/project-years/", views.ProjectYearListAPIView.as_view(), name="year-list"),  # tested
    path("project-planning/project-years/<int:pk>/", views.ProjectYearRetrieveAPIView.as_view(), name="year-detail"),  # tested
    path("project-planning/project-years/<int:project_year>/submit/", views.ProjectYearSubmitAPIView.as_view(), name="year-submit"),  # tested
    path("project-planning/project-years/<int:project_year>/unsubmit/", views.ProjectYearUnsubmitAPIView.as_view(), name="year-unsubmit"),  # tested

    # Staff
    path("project-planning/project-years/<int:project_year>/staff/", views.StaffListCreateAPIView.as_view(), name="staff-list"),  # tested
    path("project-planning/staff/<int:pk>/", views.StaffRetrieveUpdateDestroyAPIView.as_view(), name="staff-detail"),
    path("project-planning/get-dates/", views.GetDatesAPIView.as_view(), name="get-dates"),

    # O&M
    path("project-planning/project-years/<int:project_year>/om-costs/", views.OMCostListCreateAPIView.as_view(), name="om-list"),  # tested
    path("project-planning/om-costs/<int:pk>/", views.OMCostRetrieveUpdateDestroyAPIView.as_view(), name="om-detail"),
    path("project-planning/project-years/<int:project_year>/add-all-costs/", views.AddAllCostsAPIView.as_view(), name="add-all-costs"),
    path("project-planning/project-years/<int:project_year>/remove-empty-costs/", views.RemoveEmptyCostsAPIView.as_view(), name="remove-empty-costs"),

    # Capital
    path("project-planning/project-years/<int:project_year>/capital-costs/", views.CapitalCostListCreateAPIView.as_view(), name="capital-list"),  # tested
    path("project-planning/capital-costs/<int:pk>/", views.CapitalCostRetrieveUpdateDestroyAPIView.as_view(), name="capital-detail"),

    # GC
    path("project-planning/project-years/<int:project_year>/gc-costs/", views.GCCostListCreateAPIView.as_view(), name="gc-list"),  # tested
    path("project-planning/gc-costs/<int:pk>/", views.GCCostRetrieveUpdateDestroyAPIView.as_view(), name="gc-detail"),

    # activities
    path("project-planning/project-years/<int:project_year>/activities/", views.ActivityListCreateAPIView.as_view(), name="activity-list"),  # tested
    path("project-planning/activities/<int:pk>/", views.ActivityRetrieveUpdateDestroyAPIView.as_view(), name="activity-detail"),

    # collaborators
    path("project-planning/project-years/<int:project_year>/collaborators/", views.CollaboratorListCreateAPIView.as_view(), name="collaborator-list"),  # tested
    path("project-planning/collaborators/<int:pk>/", views.CollaboratorRetrieveUpdateDestroyAPIView.as_view(), name="collaborator-detail"),

    # agreements
    path("project-planning/project-years/<int:project_year>/agreements/", views.AgreementListCreateAPIView.as_view(), name="agreement-list"),  # tested
    path("project-planning/agreements/<int:pk>/", views.AgreementRetrieveUpdateDestroyAPIView.as_view(), name="agreement-detail"),

    # files
    path("project-planning/project-years/<int:project_year>/files/", views.FileListCreateAPIView.as_view(), name="file-list"),  # tested
    path("project-planning/files/<int:pk>/", views.FileRetrieveUpdateDestroyAPIView.as_view(), name="file-detail"),

    # status reports
    path("project-planning/project-years/<int:project_year>/status-reports/", views.StatusReportListCreateAPIView.as_view(), name="status-report-list"),
    # tested
    path("project-planning/status-reports/<int:pk>/", views.StatusReportRetrieveUpdateDestroyAPIView.as_view(), name="status-report-detail"),
    path("project-planning/status-reports/<int:status_report>/updates/", views.ActivityUpdateListAPIView.as_view(),
         name="activity-update-list"),
    path("project-planning/activity-updates/<int:pk>/", views.ActivityUpdateRetrieveUpdateAPIView.as_view(),
         name="activity-update-detail"),

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
