from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'publications'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    #PUBLICATIONS
    path('my-list/', views.MyPublicationsListView.as_view(), name="my_pub_list"),
    path('new/', views.PublicationsCreateView.as_view(), name="pub_new"),
    path('<int:pk>/view', views.PublicationDetailView.as_view(), name="pub_detail"),

]
