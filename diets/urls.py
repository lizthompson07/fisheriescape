from django.urls import path
from . import views

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.index, name="index"),

    # SPECIES #
    ###########
    path('species/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),

    # PREDATORS #
    #############
    path('predators/search/', views.PredatorSearchFormView.as_view(), name="predator_search"),
    path('predators/cruise=<str:cruise>/species=<str:species>/',
         views.PredatorListView.as_view(), name="predator_list"),
    # path('predators/', views.PredatorListView.as_view(), name="predator_list"),
    path('predator/new/', views.PredatorCreateView.as_view(), name="predator_new"),
    path('predator/<int:pk>/view/', views.PredatorDetailView.as_view(), name="predator_detail"),
    path('predator/<int:pk>/edit/', views.PredatorUpdateView.as_view(), name="predator_edit"),
    path('predator/<int:pk>/delete/', views.PredatorDeleteView.as_view(), name="predator_delete"),

    # PREY #
    ########
    path('predator/<int:predator>/species/insert/', views.PreyInsertView.as_view(), name="prey_search"),
    path('predator/<int:predator>/species/<int:species>/add/', views.PreyCreateView.as_view(), name="prey_new"),
    path('prey/<int:pk>/edit/', views.PreyUpdateView.as_view(), name="prey_edit"),
    path('prey/<int:pk>/delete/return-to-<str:backto>/', views.prey_delete, name="prey_delete"),

    # CRUISES #
    ###########
    path('cruises/', views.CruiseListView.as_view(), name ="cruise_list" ),
    path('cruise/new/', views.CruiseCreateView.as_view(), name ="cruise_new" ),
    path('cruise/<int:pk>/view/', views.CruiseDetailView.as_view(), name ="cruise_detail" ),
    path('cruise/<int:pk>/edit/', views.CruiseUpdateView.as_view(), name ="cruise_edit" ),
    path('cruise/<int:pk>/delete/', views.CruiseDeleteView.as_view(), name ="cruise_delete" ),

    # DIGESTION LEVELS #
    ####################
    path('digestion-levels/', views.DigestionListView.as_view(), name ="digestion_list" ),
    path('digestion-level/new/', views.DigestionCreateView.as_view(), name ="digestion_new" ),
    path('digestion-level/<int:pk>/edit/', views.DigestionUpdateView.as_view(), name ="digestion_edit" ),
    path('digestion-level/<int:pk>/delete/', views.DigestionDeleteView.as_view(), name ="digestion_delete" ),

]

app_name = 'diets'
