from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'docs'

urlpatterns = [
    path('', views.DocListView.as_view(), name='doc_list'),
    path('new/', views.DocCreateView.as_view(), name='doc_create'),
    path('edit/<int:pk>', views.DocUpdateView.as_view(), name='doc_edit'),
]

 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
