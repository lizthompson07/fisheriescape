from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),
    path('route/<int:pk>/view/', views.RouteDetailView.as_view(), name="route_detail"),

]
app_name = 'spring_cleanup'
