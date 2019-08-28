from django.conf.urls import url
from django.urls import path

from tracking.views import dashboard, user_history, app_history

urlpatterns = [
    url(r'^$', dashboard, name='tracking-dashboard'),
    path('user/<int:user>/', user_history , name="user_history"),
    path('app/<str:app>/', app_history , name="app_history")
]

app_name = "tracking"