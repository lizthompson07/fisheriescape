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


    # CRUISE SUMMARY
    # path('cruise-summary/', es_views.CruiseSummary.as_view(), name="cruise-summary"),
    #
    # # BACKUP
    # path('backup/', es_views.BackupDB.as_view(), name="backup-db"),
    # path('record-cruise-track/', shared_views.RecordTrack.as_view(), name="record-track"),
    #
    # # STATION CUE
    # path('station-cue/station-validation/', es_views.StationCueAPIView.as_view(), name="station-validation"),
    # path('station-cue/new/', es_views.StationCueAPIView.as_view(), name="station-new"),
    #
    # path('station-cue/<int:pk>/', es_views.StationCueRetrieveUpdateDestroyAPIView.as_view(), name="station-cue-detail"),
    # path('station-cue/', es_views.StationCueListAPIView.as_view(), name="station-cue-list"),
    # path('station-cue/new/', es_views.StationCueListAPIView.as_view(), name="station-cue-list"),
    #
    #
    # # ECOSYSTEM SURVEY APP
    # path('active-cruise/', es_views.ActiveCruiseAPIView.as_view(), name="active-cruise"), #TESTED
    # path('species/<int:code>/', es_views.SpeciesDetailAPIView.as_view(), name="species-detail"), #TESTED
    # path('species-by-code/<int:code>/', es_views.SpeciesDetailAPIView.as_view(), name="species-detail-using-code"), #TESTED
    # path('species/', es_views.SpeciesListAPIView.as_view(), name="species-list"),
    # path('catch/<int:pk>/', es_views.CatchDetailAPIView.as_view(), name="catch-detail"),
    # path('catch/<int:catch>/new-basket/', es_views.BasketCreateAPIView.as_view(), name="new-basket"),
    # path('catch/<int:catch>/specimens/', es_views.SpecimenListAPIView.as_view(), name="specimen-list"),
    # path('catch/<int:pk>/specimen-summary/', es_views.SpecimenSummaryAPIView.as_view(), name="specimen-summary"),
    # path('basket/<int:pk>/toggle/', es_views.BasketToggleAPIView.as_view(), name="toggle-basket"),
    # path('basket/<int:pk>/subtract-weight/', es_views.BasketSubtractWeightAPIView.as_view(), name="basket-subtract"),
    # path('basket/<int:pk>/', es_views.BasketDetailAPIView.as_view(), name="basket-detail"),
    # path('specimen/<int:pk>/', es_views.SpecimenDetailAPIView.as_view(), name="specimen-detail"),
    # path('specimen/<int:specimen>/new-observation/', es_views.ObservationCreateAPIView.as_view(), name="new-observation"),
    # path('observation/<int:pk>/', es_views.ObservationDetailAPIView.as_view(), name="observation-detail"),
    # path('observation-types/', es_views.ObservationTypeListAPIView.as_view(), name="observation-types"),
    # path('observation-types/<int:pk>/', es_views.ObservationTypeDetailAPIView.as_view(), name="observation-types-detail"),
    # path('specimen/<int:specimen>/observation-group-length-bin-lookup/', es_views.ObservationGroupLengthBinLookupAPIView.as_view(), name="length-bin-lookup"),
    # path('flag/<int:pk>/accept/', es_views.FlagAcceptAPIView.as_view(), name="flag-accept"),
    #
    # # PRINT SPECIMEN LABEL
    # path('specimen/<int:pk>/print-label/', es_views.PrintSpecimenLabelAPIView.as_view(), name="print-specimen-label"),
    #
    # # Oceanography app
    # path('new-event/', ocean_views.EventCreateAPIView.as_view(), name="event-create"),
    # path('new-bottle/', ocean_views.BottleCreateAPIView.as_view(), name="bottle-create"),
    # path('activity/<int:activity>/bottles/', ocean_views.BottleListAPIView.as_view(), name="bottle-list"),
    # path('bottle/<int:pk>/', ocean_views.BottleDetailAPIView.as_view(), name="bottle-detail"),
    # path('bottle/<int:pk>/toggle-field/', ocean_views.ToggleBottleAPIView.as_view(), name="bottle-toggle"),
    #
    # # CCG APP
    # path('current-set/', ccg_views.CurrentSetAPIView.as_view(), name="current-set"),

]

