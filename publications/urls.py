from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'publications'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    #PUBLICATIONS
    path('my-list/', views.MyPublicationsListView.as_view(), name="my_pub_list"),
    path('new/', views.PublicationCreateView.as_view(), name="pub_new"),
    path('all/', views.PublicationsListView.as_view(), name="pub_list"),
    path('<int:pk>/view', views.PublicationDetailView.as_view(), name="pub_detail"),
    path('publications/<int:pk>/edit', views.PublicationUpdateView.as_view(), name="pub_edit"),
    path('publications/<int:pk>/delete', views.PublicationDeleteView.as_view(), name="pub_delete"),
    path('publications/<int:pk>/submit', views.PublicationSubmitUpdateView.as_view(), name="pub_submit"),

]
