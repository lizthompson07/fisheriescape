from django.conf.urls import url
from django.urls import path

from tracking.views import dashboard, user_history

urlpatterns = [
    url(r'^$', dashboard, name='tracking-dashboard'),
    path('user/<int:user>/', user_history , name="user_history")
]

app_name = "tracking"