from django.urls import path
from . import views

app_name = 'bio_diversity'

urlpatterns = [
    # for home/index page
    path('', views.IndexTemplateView.as_view(),    name="index"),

    path('create/inst/', views.InstCreate.as_view(), name="create_inst"),
    path('details/inst/<int:pk>/', views.InstDetails.as_view(), name="details_inst"),
    path('list/inst/', views.InstList.as_view(), name="list_inst"),
    path('update/inst/<int:pk>/', views.InstUpdate.as_view(), name="update_inst"),

    path('create/instc/', views.InstcCreate.as_view(), name="create_instc"),
    path('details/instc/<int:pk>/', views.InstcDetails.as_view(), name="details_instc"),
    path('list/instc/', views.InstcList.as_view(), name="list_instc"),
    path('update/instc/<int:pk>/', views.InstcUpdate.as_view(), name="update_instc"),

    path('create/instdc/', views.InstdcCreate.as_view(), name="create_instdc"),
    path('details/instdc/<int:pk>/', views.InstdcDetails.as_view(), name="details_instdc"),
    path('list/instdc/', views.InstdcList.as_view(), name="list_instdc"),
    path('update/instdc/<int:pk>/', views.InstdcUpdate.as_view(), name="update_instdc"),

]