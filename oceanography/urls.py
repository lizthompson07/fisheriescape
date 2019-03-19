from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'oceanography'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),

    # DOC LIBRARY #
    ###############
    path('docs/', views.DocListView.as_view(), name='doc_list'),
    path('docs/new/', views.DocCreateView.as_view(), name='doc_create'),
    path('docs/edit/<int:pk>', views.DocUpdateView.as_view(), name='doc_edit'),

    # MISSIONS #
    ############
    path('missions/', views.MissionYearListView.as_view(), name='mission_year_list'),
    path('missions/<int:year>/list/', views.MissionListView.as_view(), name='mission_list'),
    path('mission/<int:pk>/view/', views.MissionDetailView.as_view(), name='mission_detail'),
    path('mission/<int:pk>/edit/', views.MissionUpdateView.as_view(), name='mission_edit'),
    path('mission/<int:year>/new/', views.MissionCreateView.as_view(), name='mission_new'),
    path('mission/<int:pk>/export-csv/', views.export_mission_csv, name='mission_export_csv'),

    # BOTTLES #
    ###########
    path('missions/<int:mission>/bottles/', views.BottleListView.as_view(), name='bottle_list'),
    path('bottles/<int:pk>/view/', views.BottleDetailView.as_view(), name='bottle_detail'),
    path('bottles/<int:pk>/edit/', views.BottleUpdateView.as_view(), name='bottle_edit'),

    # FILES #
    #########
    path('mission/<int:mission>/file/new/', views.FileCreateView.as_view(), name='file_create'),
    path('file/<int:pk>/view/', views.FileDetailView.as_view(), name='file_detail'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

]

 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
