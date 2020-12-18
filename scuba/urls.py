from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),
    
    # reference tables
    path('settings/divers/', views.DiverFormsetView.as_view(), name="manage_divers"),
    path('settings/diver/<int:pk>/delete/', views.DiverHardDeleteView.as_view(), name="delete_diver"),
    
    # regions
    path('regions/', views.RegionListView.as_view(), name="region_list"),
    path('regions/new/', views.RegionCreateView.as_view(), name="region_new"),
    path('regions/<int:pk>/view/', views.RegionDetailView.as_view(), name="region_detail"),
    path('regions/<int:pk>/edit/', views.RegionUpdateView.as_view(), name="region_edit"),
    path('regions/<int:pk>/delete/', views.RegionDeleteView.as_view(), name="region_delete"),

    path('regions/<int:region>/new-site/', views.SiteCreateView.as_view(), name="site_new"),
    path('sites/<int:pk>/edit/', views.SiteUpdateView.as_view(), name="site_edit"),
    path('sites/<int:pk>/delete/', views.SiteDeleteView.as_view(), name="site_delete"),


]

app_name = 'scuba'
