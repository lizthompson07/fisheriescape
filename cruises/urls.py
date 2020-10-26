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
    path('missions/', views.MissionListView.as_view(), name='mission_list'),
    path('mission/<int:pk>/view/', views.MissionDetailView.as_view(), name='mission_detail'),
    path('mission/<int:pk>/edit/', views.MissionUpdateView.as_view(), name='mission_edit'),
    path('mission/new/', views.MissionCreateView.as_view(), name='mission_new'),
    path('mission/<int:pk>/export-csv/', views.export_mission_csv, name='mission_export_csv'),

    # FILES #
    #########
    path('mission/<int:mission>/file/new/', views.FileCreateView.as_view(), name='file_create'),
    path('file/<int:pk>/view/', views.FileDetailView.as_view(), name='file_detail'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

]

 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
