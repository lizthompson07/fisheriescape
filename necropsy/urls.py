from . import views
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'necropsy'

urlpatterns = [
    path('', views.index, name="index"),


#     # Inventory #
#     ###########
    path('item_list/', views.ItemsListView.as_view(), name="item_list"),
    path('item_detail/<int:pk>/view/', views.ItemsDetailView.as_view(), name="item_detail")
#     # path('species/new/', views.SpeciesCreateView.as_view(), name="item_new"),
#     # path('species/<int:pk>/edit/', views.SpeciesUpdateView.as_view(), name="item_edit"),
#     # path('species/<int:pk>/delete/', views.SpeciesDeleteView.as_view(), name="item_delete"),


]

