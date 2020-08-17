from django.urls import path
from . import views

app_name = 'engagements'

urlpatterns = [
    path('', views.engagements_home, name='home'),
]