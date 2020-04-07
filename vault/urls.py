
from . import views

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'vault'

urlpatterns = [
    path('', views.index, name="index"),

    # path('admin/', admin.site.urls),

#     # DASHBOARD 1 #
#     ###########

    path('dashboard/', views.dashboard_with_pivot, name="dashboard_with_pivot"),
    path('data/', views.pivot_data, name="pivot_data"),

#     # SPECIES #
#     ###########
    path('species-list/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),
    #

    # # OBSERVAION PLATFORMS #
    # #############
    path('observationplatform-list/', views.ObservationPlatformListView.as_view(), name="observationplatform_list"),
    path('observationplatform/new/', views.ObservationPlatformCreateView.as_view(), name="observationplatform_new"),
    path('observationplatform/<int:pk>/view/', views.ObservationPlatformDetailView.as_view(), name="observationplatform_detail"),
    path('observationplatform/<int:pk>/edit/', views.ObservationPlatformUpdateView.as_view(), name="observationplatform_edit"),
    path('observationplatform/<int:pk>/delete/', views.ObservationPlatformDeleteView.as_view(), name="observationplatform_delete"),

    # # INSTRUMENTS #
    path('instrument-list/', views.InstrumentListView.as_view(), name="instrument_list"),
    path('instrument/new/', views.InstrumentCreateView.as_view(), name="instrument_new"),
    path('instrument/<int:pk>/view/', views.InstrumentDetailView.as_view(), name="instrument_detail"),
    path('instrument/<int:pk>/edit/', views.InstrumentUpdateView.as_view(), name="instrument_edit"),
    path('instrument/<int:pk>/delete/', views.InstrumentDeleteView.as_view(), name="instrument_delete"),

    # # OUTING #
    path('outing-list/', views.OutingListView.as_view(), name="outing_list"),
    path('outing/new/', views.OutingCreateView.as_view(), name="outing_new"),
    path('outing/<int:pk>/view/', views.OutingDetailView.as_view(), name="outing_detail"),
    path('outing/<int:pk>/edit/', views.OutingUpdateView.as_view(), name="outing_edit"),
    path('outing/<int:pk>/delete/', views.OutingDeleteView.as_view(), name="outing_delete"),

    # # PERSON #
    path('person-list/', views.PersonListView.as_view(), name="person_list"),
    path('person/new/', views.PersonCreateView.as_view(), name="person_new"),
    path('person/<int:pk>/view/', views.PersonDetailView.as_view(), name="person_detail"),
    path('person/<int:pk>/edit/', views.PersonUpdateView.as_view(), name="person_edit"),
    path('person/<int:pk>/delete/', views.PersonDeleteView.as_view(), name="person_delete"),

]


