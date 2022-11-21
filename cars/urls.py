from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),
    path('faq/', views.FAQListView.as_view(), name="faq"),

    # reference tables
    path('settings/vehicle-types/', views.VehicleTypeFormsetView.as_view(), name="manage_vehicle_types"),
    path('settings/vehicle-type/<int:pk>/delete/', views.VehicleTypeHardDeleteView.as_view(), name="delete_vehicle_type"),
    path('settings/locations/', views.LocationFormsetView.as_view(), name="manage_locations"),
    path('settings/location/<int:pk>/delete/', views.LocationHardDeleteView.as_view(), name="delete_location"),
    path('settings/vehicles/', views.VehicleFormsetView.as_view(), name="manage_vehicles"),
    path('settings/vehicle/<int:pk>/delete/', views.VehicleHardDeleteView.as_view(), name="delete_vehicle"),
    path('settings/faqs/', views.FAQFormsetView.as_view(), name="manage_faqs"),
    path('settings/faq/<int:pk>/delete/', views.FAQHardDeleteView.as_view(), name="delete_faq"),

    # full
    path('settings/reference-materials/', views.ReferenceMaterialListView.as_view(), name="ref_mat_list"),
    path('settings/reference-materials/new/', views.ReferenceMaterialCreateView.as_view(), name="ref_mat_new"),
    path('settings/reference-materials/<int:pk>/edit/', views.ReferenceMaterialUpdateView.as_view(), name="ref_mat_edit"),
    path('settings/reference-materials/<int:pk>/delete/', views.ReferenceMaterialDeleteView.as_view(), name="ref_mat_delete"),

    # user permissions
    path('settings/users/', views.CarsUserFormsetView.as_view(), name="manage_cars_users"),
    path('settings/users/<int:pk>/delete/', views.CarsUserHardDeleteView.as_view(), name="delete_cars_user"),

    # vehicles
    path('find-a-vehicle/', views.VehicleFinder.as_view(), name="vehicle_finder"),
    path('fleet/', views.VehicleListView.as_view(), name="vehicle_list"),
    path('calendar/', views.VehicleCalendarView.as_view(), name="calendar"),
    path('vehicles/new/', views.VehicleCreateView.as_view(), name="vehicle_new"),
    path('vehicles/<int:pk>/edit/', views.VehicleUpdateView.as_view(), name="vehicle_edit"),
    path('vehicles/<int:pk>/delete/', views.VehicleDeleteView.as_view(), name="vehicle_delete"),
    path('vehicles/<int:pk>/view/', views.VehicleDetailView.as_view(), name="vehicle_detail"),

    # reservations
    path('reservations/', views.ReservationListView.as_view(), name="rsvp_list"),
    path('reservations/new/', views.ReservationCreateView.as_view(), name="rsvp_new"),
    path('reservations/<int:pk>/edit/', views.ReservationUpdateView.as_view(), name="rsvp_edit"),
    path('reservations/<int:pk>/delete/', views.ReservationDeleteView.as_view(), name="rsvp_delete"),
    path('reservations/<int:pk>/view/', views.ReservationDetailView.as_view(), name="rsvp_detail"),
    path('reservations/<int:pk>/<str:action>/', views.rsvp_action, name="rsvp_action"),



    # # reports
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),  # tested

]

app_name = 'cars'
