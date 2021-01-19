from django.urls import path
from . import views

from django.contrib.gis import admin

app_name = "fisheriescape"

urlpatterns = [
    path('admin', admin.site.urls),
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.index, name="index"),

    # MAP #
    path('map/', views.MapView.as_view(), name="map_view"),

    # SPECIES #

    path('species-list/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),

    # FISHERY AREA #

    path('fisheryarea-list/', views.FisheryAreaListView.as_view(), name="fishery_area_list"),
    path('fisheryarea/new/', views.FisheryAreaCreateView.as_view(), name="fishery_area_new"),
    path('fisheryarea/<int:pk>/view/', views.FisheryAreaDetailView.as_view(), name="fishery_area_detail"),
    path('fisheryarea/<int:pk>/edit/', views.FisheryAreaUpdateView.as_view(), name="fishery_area_edit"),
    path('fisheryarea/<int:pk>/delete/', views.FisheryAreaDeleteView.as_view(), name="fishery_area_delete"),

]
