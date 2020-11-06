from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'project-years', views.ProjectYearViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("user/", views.CurrentUserAPIView.as_view(), name="current-user"),

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
