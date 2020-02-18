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
    path('item_list/', views.ItemListView.as_view(), name="item_list"),
    path('item_detail/<int:pk>/view/', views.ItemDetailView.as_view(), name="item_detail"),
    path('item/new/', views.ItemCreateView.as_view(), name="item_new"),
    path('item/<int:pk>/edit/', views.ItemUpdateView.as_view(), name="item_edit"),
    path('item/<int:pk>/delete/', views.ItemDeleteView.as_view(), name="item_delete"),


]

