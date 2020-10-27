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
    path('cruises/', views.CruiseListView.as_view(), name='cruise_list'),
    path('cruise/<int:pk>/view/', views.CruiseDetailView.as_view(), name='cruise_detail'),
    path('cruise/<int:pk>/edit/', views.CruiseUpdateView.as_view(), name='cruise_edit'),
    path('cruise/new/', views.CruiseCreateView.as_view(), name='cruise_new'),
    # path('cruise/<int:pk>/export-csv/', views.export_cruise_csv, name='cruise_export_csv'),

    # FILES #
    #########
    path('cruise/<int:cruise>/file/new/', views.FileCreateView.as_view(), name='file_create'),
    path('file/<int:pk>/view/', views.FileDetailView.as_view(), name='file_detail'),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name='file_edit'),
    path('file/<int:pk>/delete/', views.FileDeleteView.as_view(), name='file_delete'),

]

 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
