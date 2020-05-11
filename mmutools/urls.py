from . import views
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'mmutools'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.index, name="index"),


#     # ITEMS #
#     ###########
    path('item_list/', views.ItemListView.as_view(), name="item_list"),
    path('item_detail/<int:pk>/view/', views.ItemDetailView.as_view(), name="item_detail"),
    path('item/new/', views.ItemCreateView.as_view(), name="item_new"),
    path('item/<int:pk>/edit/', views.ItemUpdateView.as_view(), name="item_edit"),
    path('item/<int:pk>/delete/', views.ItemDeleteView.as_view(), name="item_delete"),

# QUANTITIES #

    path('quantity_list/', views.QuantityListView.as_view(), name="quantity_list"),
    path('quantity_detail/<int:pk>/view/', views.QuantityDetailView.as_view(), name="quantity_detail"),
    path('item/<int:pk>/quantity/new/', views.QuantityCreateView.as_view(), name="quantity_new"),
    path('quantity/new/', views.QuantityCreateView.as_view(), name="quantity_new"),
    path('quantity/<int:pk>/edit/', views.QuantityUpdateView.as_view(), name="quantity_edit"),
    path('quantity/<int:pk>/edit/pop/<int:pop>/', views.QuantityUpdateView.as_view(), name="quantity_edit"),
    path('quantity/<int:pk>/delete/pop/<int:pop>/', views.QuantityDeleteView.as_view(), name="quantity_delete"),
    path('quantity/<int:pk>/delete/', views.QuantityDeleteView.as_view(), name="quantity_delete"),

# LOCATION #

    path('location_list/', views.LocationListView.as_view(), name="location_list"),
    path('location_detail/<int:pk>/view/', views.LocationDetailView.as_view(), name="location_detail"),
    path('location/new/', views.LocationCreateView.as_view(), name="location_new"),
    path('location/<int:pk>/edit/', views.LocationUpdateView.as_view(), name="location_edit"),
    path('location/<int:pk>/delete/', views.LocationDeleteView.as_view(), name="location_delete"),

# PERSONNEL #

    path('personnel_list/', views.PersonnelListView.as_view(), name="personnel_list"),
    path('personnel_detail/<int:pk>/view/', views.PersonnelDetailView.as_view(), name="personnel_detail"),
    path('personnel/new/', views.PersonnelCreateView.as_view(), name="personnel_new"),
    path('personnel/<int:pk>/edit/', views.PersonnelUpdateView.as_view(), name="personnel_edit"),
    path('personnel/<int:pk>/delete/', views.PersonnelDeleteView.as_view(), name="personnel_delete"),

# SUPPLIER #

    path('supplier_list/', views.SupplierListView.as_view(), name="supplier_list"),
    path('supplier_detail/<int:pk>/view/', views.SupplierDetailView.as_view(), name="supplier_detail"),
    path('supplier/new/', views.SupplierCreateView.as_view(), name="supplier_new"),
    path('item/<int:pk>/supplier/new/', views.SupplierCreateView.as_view(), name="supplier_new"),
    path('supplier/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name="supplier_edit"),
    path('supplier/<int:pk>/edit/pop/<int:pop>/', views.SupplierUpdateView.as_view(), name="supplier_edit"),
    path('supplier/<int:pk>/delete/pop/<int:pop>/', views.SupplierDeleteView.as_view(), name="supplier_delete"),
    path('supplier/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name="supplier_delete"),

# ITEM FILES #

    path('item/<int:item>/file/new/', views.FileCreateView.as_view(), name="file_new"),
    path('file/<int:pk>/view/', views.FileDetailView.as_view(), name="file_detail"),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name="file_edit"),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name="file_delete"),

# LENDING #

    path('lending_list/', views.LendingListView.as_view(), name="lending_list"),
    path('lending_detail/<int:pk>/view/', views.LendingDetailView.as_view(), name="lending_detail"),
    path('lending/new/', views.LendingCreateView.as_view(), name="lending_new"),
    path('lending/<int:pk>/edit/', views.LendingUpdateView.as_view(), name="lending_edit"),
    path('lending/<int:pk>/delete/', views.LendingDeleteView.as_view(), name="lending_delete"),

# INCIDENT #

    path('incident_list/', views.IncidentListView.as_view(), name="incident_list"),
    path('incident_detail/<int:pk>/view/', views.IncidentDetailView.as_view(), name="incident_detail"),
    path('incident/new/', views.IncidentCreateView.as_view(), name="incident_new"),
    path('incident/<int:pk>/edit/', views.IncidentUpdateView.as_view(), name="incident_edit"),
    path('incident/<int:pk>/delete/', views.IncidentDeleteView.as_view(), name="incident_delete"),

]

