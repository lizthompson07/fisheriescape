
from . import views

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'vault'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.index, name="index"),

#     # DASHBOARD 1 #
#     ###########

    # path('dashboard/', views.dashboard_with_pivot, name="dashboard_with_pivot"),
    # path('data/', views.pivot_data, name="pivot_data"),

    # SETTINGS #

    path('admin_tools', views.admin_tools, name="admin_tools"),


    # ADMIN USERS #
    path('settings/users/', views.UserListView.as_view(), name='user_list'),
    path('settings/users/vault/<int:vault>/', views.UserListView.as_view(), name='user_list'),
    path('settings/user/<int:pk>/toggle/<str:type>/', views.toggle_user, name='toggle_user'),

    # SPECIES #

    path('species-list/', views.SpeciesListView.as_view(), name="species_list"),
    path('species/new/', views.SpeciesCreateView.as_view(), name="species_new"),
    path('species/<int:pk>/view/', views.SpeciesDetailView.as_view(), name="species_detail"),
    path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="species_edit"),
    path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="species_delete"),



]


