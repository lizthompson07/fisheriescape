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
from accounts import views as acc_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name="index"),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('dm-tickets/', include('dm_tickets.urls')),
    path('oceanography/', include('oceanography.urls')),
    path('grais/', include('grais.urls')),
    path('hermorrhage/', include('herring.urls')),
    path('bugs/', include('bugs.urls')),
    path('camp/', include('camp.urls')),
    path('snowcrab/', include('snowcrab.urls')),

    # Password reset views. Views are part of accounts app #
    ########################################################

    path('password-reset/', acc_views.UserPassWordResetView.as_view(), name='password_reset'),
    path('reset/<str:uidb64>/<str:token>/', acc_views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', acc_views.IndexView.as_view(), name='password_reset_complete'),
]

if settings.MY_ENVR == "dev":
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
