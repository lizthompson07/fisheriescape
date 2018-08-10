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
from django.contrib import admin
from django.urls import path, include
from . import views as site_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', site_views.HomePage.as_view(), name='home'),
    path('contact/', site_views.Contact.as_view(), name='contact'),
    path('apps/', site_views.Apps.as_view(), name='apps'),
    path('docs/', include('docs.urls')),
]
# 
# # if in dev mode, you will have to map out the media file.
# from . import media_conf
# if media_conf.where_am_i() == "development":
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
