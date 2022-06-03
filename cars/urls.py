from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # reference tables
    path('settings/vehicle-types/', views.VehicleTypeFormsetView.as_view(), name="manage_vehicle_types"),
    path('settings/vehicle-type/<int:pk>/delete/', views.VehicleTypeHardDeleteView.as_view(), name="delete_vehicle_type"),
    path('settings/locations/', views.LocationFormsetView.as_view(), name="manage_locations"),
    path('settings/location/<int:pk>/delete/', views.LocationHardDeleteView.as_view(), name="delete_location"),

    # user permissions
    path('settings/users/', views.CarsUserFormsetView.as_view(), name="manage_cars_users"),
    path('settings/users/<int:pk>/delete/', views.CarsUserHardDeleteView.as_view(), name="delete_cars_user"),

    # vehicles
    path('vehicles/', views.VehicleListView.as_view(), name="vehicle_list"),
    path('vehicles/new/', views.VehicleCreateView.as_view(), name="vehicle_new"),
    path('vehicles/<int:pk>/edit/', views.VehicleUpdateView.as_view(), name="vehicle_edit"),
    path('vehicles/<int:pk>/delete/', views.VehicleDeleteView.as_view(), name="vehicle_delete"),
    path('vehicles/<int:pk>/view/', views.VehicleDetailView.as_view(), name="vehicle_detail"),



    # # reports
    # path('reports/', views.ReportSearchFormView.as_view(), name="reports"),  # tested

]

app_name = 'cars'
