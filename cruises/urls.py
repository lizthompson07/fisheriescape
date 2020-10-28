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
    path('list/', views.CruiseListView.as_view(), name='cruise_list'),# TESTED
    path('new/', views.CruiseCreateView.as_view(), name='cruise_new'),# TESTED
    path('<int:pk>/view/', views.CruiseDetailView.as_view(), name='cruise_detail'),# TESTED
    path('<int:pk>/edit/', views.CruiseUpdateView.as_view(), name='cruise_edit'),# TESTED
    path('<int:pk>/delete/', views.CruiseDeleteView.as_view(), name='cruise_delete'),# TESTED
    # path('cruise/<int:pk>/export-csv/', views.export_cruise_csv, name='cruise_export_csv'),

    # FILES #
    #########
    path('<int:cruise>/file/new/', views.FileCreateView.as_view(), name='file_new'),# TESTED
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),# TESTED
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),# TESTED

    # SETTINGS #
    ############
    path('settings/vessels/', views.VesselFormsetView.as_view(), name="manage_vessels"),# TESTED
    path('settings/vessel/<int:pk>/delete/', views.VesselHardDeleteView.as_view(), name="delete_vessel"),# TESTED

    path('settings/institutes/', views.InstituteFormsetView.as_view(), name="manage_institutes"),# TESTED
    path('settings/institute/<int:pk>/delete/', views.InstituteHardDeleteView.as_view(), name="delete_institute"),# TESTED

]

 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
