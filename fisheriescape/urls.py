from django.urls import path
from django.contrib.gis import admin

from . import views

app_name = "fisheriescape"

urlpatterns = [
    path('admin', admin.site.urls),
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexView.as_view(), name="index"),

    # MAP #
    path('map/', views.MapView.as_view(), name="map_view"),

    # FISHERY AREA #

    path('fisheryarea-list/', views.FisheryAreaListView.as_view(), name="fishery_area_list"),
    # path('fisheryarea/new/', views.FisheryAreaCreateView.as_view(), name="fishery_area_new"),
    path('fisheryarea/<int:pk>/view/', views.FisheryAreaDetailView.as_view(), name="fishery_area_detail"),
    # path('fisheryarea/<int:pk>/edit/', views.FisheryAreaUpdateView.as_view(), name="fishery_area_edit"),
    # path('fisheryarea/<int:pk>/delete/', views.FisheryAreaDeleteView.as_view(), name="fishery_area_delete"),

    # NAFO AREA #

    path('nafoarea-list/', views.NAFOAreaListView.as_view(), name="nafo_area_list"),
    path('nafoarea/<int:pk>/view/', views.NAFOAreaDetailView.as_view(), name="nafo_area_detail"),

    # FISHERY #

    path('fishery-list/', views.FisheryListView.as_view(), name="fishery_list"),
    path('fishery/new/', views.FisheryCreateView.as_view(), name="fishery_new"),
    path('fishery/<int:pk>/view/', views.FisheryDetailView.as_view(), name="fishery_detail"),
    path('fishery/<int:pk>/edit/', views.FisheryUpdateView.as_view(), name="fishery_edit"),
    path('fishery/<int:pk>/delete/', views.FisheryDeleteView.as_view(), name="fishery_delete"),

    # SCORES #
    path('scores-map/', views.ScoreMapView.as_view(), name="score_map"),

    # IMPORTS #
    path('import/vulnerable-species-spots', views.ImportVulnerableSpeciesSpotsView.as_view(),
         name="import_vulnerable_species_spots"),

    path('import/fisheriescape-scores', views.ImportFisheriescapeScoresView.as_view(),
         name="import_fisheriescape_scores"),

    # SETTINGS #
    ############

    path('settings/marinemammals/', views.MarineMammalFormsetView.as_view(), name="manage_marinemammals"),
    path('settings/marinemammals/<int:pk>/delete/', views.MarineMammalHardDeleteView.as_view(),
         name="delete_marinemammals"),
    path('settings/species/', views.SpeciesFormsetView.as_view(), name="manage_species"),
    path('settings/species/<int:pk>/delete/', views.SpeciesHardDeleteView.as_view(), name="delete_species"),

    # ADMIN USERS #
    path('settings/users/', views.UserListView.as_view(), name='user_list'),
    path('settings/users/fisheriescape/<int:fisheriescape>/', views.UserListView.as_view(), name='user_list'),
    path('settings/user/<int:pk>/toggle/<str:type>/', views.toggle_user, name='toggle_user'),

]
