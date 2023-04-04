"""dm_apps URL Configuration

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

import debug_toolbar
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from accounts import views as acc_views
from . import views as views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('api/shared/', include('shared_models.api.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    # path('api/tracking/', include('tracking.api.urls')),
]

# Add application APIs

if settings.INSTALLED_APPS.count("fisheriescape"):
    urlpatterns.append(
        path('api/', include('fisheriescape.api.urls')),
    )



urlpatterns += i18n_patterns(
    path('', views.IndexView.as_view(), name="index"),
    path('accounts/', include('accounts.urls')),
    path('shared/', include('shared_models.urls')),
    # path('tracking/', include('tracking.urls')),
    prefix_default_language=True)

if settings.INSTALLED_APPS.count("tickets"):
    urlpatterns += i18n_patterns(path('dm-tickets/', include('tickets.urls')), prefix_default_language=True)
else:
    print("not connecting ticket app")

if settings.INSTALLED_APPS.count("fisheriescape"):
    urlpatterns += i18n_patterns(path('fisheriescape/', include('fisheriescape.urls')),
                                 prefix_default_language=True)
else:
    print("not connecting fisheriescape app")

if settings.AZURE_STORAGE_ACCOUNT_NAME == "":
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                            document_root=settings.MEDIA_ROOT)
# print(urlpatterns)
