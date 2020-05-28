from . import views
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'whalebrary'

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

# BULK QUANTITIES #

    path('bulk_quantity_list/', views.BulkQuantityListView.as_view(), name="bulk_quantity_list"),
    # path('bulk_quantity_detail/<int:pk>/view/', views.BulkQuantityDetailView.as_view(), name="bulk_quantity_detail"),
    path('quantity/<int:pk>/delete/', views.BulkQuantityDeleteView.as_view(), name="bulk_quantity_delete"),

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


# INCIDENT #

    path('incident_list/', views.IncidentListView.as_view(), name="incident_list"),
    path('incident_detail/<int:pk>/view/', views.IncidentDetailView.as_view(), name="incident_detail"),
    path('incident/new/', views.IncidentCreateView.as_view(), name="incident_new"),
    path('incident/<int:pk>/edit/', views.IncidentUpdateView.as_view(), name="incident_edit"),
    path('incident/<int:pk>/delete/', views.IncidentDeleteView.as_view(), name="incident_delete"),

# REPORTS #

    path('reports/generator/', views.ReportGeneratorFormView.as_view(), name="report_generator"),
    path('reports/generator/<int:report_number>/', views.ReportGeneratorFormView.as_view(), name="report_generator"),
    path('reports/container_summary/location/<int:location>/', views.ContainerSummaryListView.as_view(), name="report_container"),
    path('reports/sized_item_summary/item_name/<slug:item_name>/', views.SizedItemSummaryListView.as_view(), name="report_sized_item"),

]

