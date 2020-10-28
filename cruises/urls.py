from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'cruises'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'), # TESTED


    # MISSIONS #
    ############
    path('list/', views.CruiseListView.as_view(), name='cruise_list'),
    path('new/', views.CruiseCreateView.as_view(), name='cruise_new'),
    path('<int:pk>/view/', views.CruiseDetailView.as_view(), name='cruise_detail'),
    path('<int:pk>/edit/', views.CruiseUpdateView.as_view(), name='cruise_edit'),
    path('<int:pk>/delete/', views.CruiseDeleteView.as_view(), name='cruise_delete'),
    # path('cruise/<int:pk>/export-csv/', views.export_cruise_csv, name='cruise_export_csv'),

    # FILES #
    #########
    path('<int:cruise>/file/new/', views.FileCreateView.as_view(), name='file_create'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

    # SETTINGS #
    ############
    path('settings/vessels/', views.VesselFormsetView.as_view(), name="manage_vessels"),
    path('settings/vessel/<int:pk>/delete/', views.VesselHardDeleteView.as_view(), name="delete_vessel"),

    path('settings/institutes/', views.InstituteFormsetView.as_view(), name="manage_institutes"),
    path('settings/institute/<int:pk>/delete/', views.InstituteHardDeleteView.as_view(), name="delete_institute"),


]

 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
