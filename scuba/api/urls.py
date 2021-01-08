from django.urls import path

from . import views

urlpatterns = [
    path("scuba/user/", views.CurrentUserAPIView.as_view(), name="current-user"),

    # observations
    path("scuba/observations/", views.ObservationListAPIView.as_view(), name="observation-list"),
    path("scuba/sections/", views.SectionListCreateAPIView.as_view(), name="section-list"),
    path("scuba/sections/<int:pk>/", views.SectionRetrieveUpdateDestroyAPIView.as_view(), name="section-list"),
    # path("scuba/projects/", views.ProjectListAPIView.as_view(), name="project-list"),  # tested
    #
    # # Project year
    # path("scuba/project-years/", views.ProjectYearListAPIView.as_view(), name="year-list"),  # tested
    # path("scuba/project-years/<int:pk>/", views.ProjectYearRetrieveAPIView.as_view(), name="year-detail"),  # tested
    # path("scuba/project-years/<int:project_year>/submit/", views.ProjectYearSubmitAPIView.as_view(), name="year-submit"),  # tested
    # path("scuba/project-years/<int:project_year>/unsubmit/", views.ProjectYearUnsubmitAPIView.as_view(), name="year-unsubmit"),  # tested
    #
    # # Staff
    # path("scuba/project-years/<int:project_year>/staff/", views.StaffListCreateAPIView.as_view(), name="staff-list"),  # tested
    # path("scuba/staff/<int:pk>/", views.StaffRetrieveUpdateDestroyAPIView.as_view(), name="staff-detail"),
    # path("scuba/get-dates/", views.GetDatesAPIView.as_view(), name="get-dates"),
    #
    # # O&M
    # path("scuba/project-years/<int:project_year>/om-costs/", views.OMCostListCreateAPIView.as_view(), name="om-list"),  # tested
    # path("scuba/om-costs/<int:pk>/", views.OMCostRetrieveUpdateDestroyAPIView.as_view(), name="om-detail"),
    # path("scuba/project-years/<int:project_year>/add-all-costs/", views.AddAllCostsAPIView.as_view(), name="add-all-costs"),
    # path("scuba/project-years/<int:project_year>/remove-empty-costs/", views.RemoveEmptyCostsAPIView.as_view(), name="remove-empty-costs"),
    #
    # # Capital
    # path("scuba/project-years/<int:project_year>/capital-costs/", views.CapitalCostListCreateAPIView.as_view(), name="capital-list"),  # tested
    # path("scuba/capital-costs/<int:pk>/", views.CapitalCostRetrieveUpdateDestroyAPIView.as_view(), name="capital-detail"),
    #
    # # GC
    # path("scuba/project-years/<int:project_year>/gc-costs/", views.GCCostListCreateAPIView.as_view(), name="gc-list"),  # tested
    # path("scuba/gc-costs/<int:pk>/", views.GCCostRetrieveUpdateDestroyAPIView.as_view(), name="gc-detail"),
    #
    # # activities
    # path("scuba/project-years/<int:project_year>/activities/", views.ActivityListCreateAPIView.as_view(), name="activity-list"),  # tested
    # path("scuba/activities/<int:pk>/", views.ActivityRetrieveUpdateDestroyAPIView.as_view(), name="activity-detail"),
    #
    # # collaborators
    # path("scuba/project-years/<int:project_year>/collaborators/", views.CollaboratorListCreateAPIView.as_view(), name="collaborator-list"),  # tested
    # path("scuba/collaborators/<int:pk>/", views.CollaboratorRetrieveUpdateDestroyAPIView.as_view(), name="collaborator-detail"),
    #
    # # agreements
    # path("scuba/project-years/<int:project_year>/agreements/", views.AgreementListCreateAPIView.as_view(), name="agreement-list"),  # tested
    # path("scuba/agreements/<int:pk>/", views.AgreementRetrieveUpdateDestroyAPIView.as_view(), name="agreement-detail"),
    #
    # # files
    # path("scuba/project-years/<int:project_year>/files/", views.FileListCreateAPIView.as_view(), name="file-list"),  # tested
    # path("scuba/files/<int:pk>/", views.FileRetrieveUpdateDestroyAPIView.as_view(), name="file-detail"),
    #
    # # status reports
    # path("scuba/project-years/<int:project_year>/status-reports/", views.StatusReportListCreateAPIView.as_view(), name="status-report-list"),
    # # tested
    # path("scuba/status-reports/<int:pk>/", views.StatusReportRetrieveUpdateDestroyAPIView.as_view(), name="status-report-detail"),
    # path("scuba/status-reports/<int:status_report>/updates/", views.ActivityUpdateListAPIView.as_view(),
    #      name="activity-update-list"),
    # path("scuba/activity-updates/<int:pk>/", views.ActivityUpdateRetrieveUpdateAPIView.as_view(),
    #      name="activity-update-detail"),
    #
    # # financials
    # path("scuba/project-years/<int:project_year>/financials/", views.FinancialsAPIView.as_view(), name="financials"),
    # path("scuba/projects/<int:project>/financials/", views.FinancialsAPIView.as_view(), name="financials"),
    # path("scuba/financials/", views.FinancialsAPIView.as_view(), name="financials"),
    #
    # # lookups
    # path("scuba/fiscal-years/", views.FiscalYearListAPIView.as_view(), name="fiscal-year-list"),
    # path("scuba/tags/", views.TagListAPIView.as_view(), name="tag-list"),
    # path("scuba/themes/", views.ThemeListAPIView.as_view(), name="theme-list"),
    # path("scuba/functional-groups/", views.FunctionalGroupListAPIView.as_view(), name="group-list"),
    # path("scuba/funding-sources/", views.FundingSourceListAPIView.as_view(), name="funding-source-list"),
    # path("scuba/regions/", views.RegionListAPIView.as_view(), name="region-list"),
    # path("scuba/divisions/", views.DivisionListAPIView.as_view(), name="division-list"),
    # path("scuba/sections/", views.SectionListAPIView.as_view(), name="section-list"),
    #
    # # Reviews
    # path("scuba/project-years/<int:project_year>/reviews/", views.ReviewListCreateAPIView.as_view(), name="review-list"),
    # path("scuba/reviews/<int:pk>/", views.ReviewRetrieveUpdateDestroyAPIView.as_view(), name="review-detail"),

]
