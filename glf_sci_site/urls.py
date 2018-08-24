"""glf_sci_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views as views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name="index"),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('dm-tickets/', include('dm_tickets.urls')),
    path('docs/', include('docs.urls')),

    path('grais/', include('grais.urls')),
    path('bugs/', include('bugs.urls')),
    path('password-reset/', auth_views.password_reset, name='password_reset'),
    path('password-reset-done/', auth_views.password_reset_done, name='password_reset_done'),
    path('reset/<str:uidb64>/<str:token>/', auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', auth_views.password_reset_complete, name='password_reset_complete'),
]

if settings.MY_ENVR == "dev":
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
