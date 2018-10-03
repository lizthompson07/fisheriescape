from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'oceanography'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),

    # DOC LIBRARY #
    ###############
    path('docs/', views.DocListView.as_view(), name='doc_list'),
    path('docs/new/', views.DocCreateView.as_view(), name='doc_create'),
    path('docs/edit/<int:pk>', views.DocUpdateView.as_view(), name='doc_edit'),

    # MISSIONS #
    ############
    path('missions/', views.MissionYearListView.as_view(), name='mission_year_list'),
    path('missions/<int:year>/list/', views.MissionListView.as_view(), name='mission_list'),
    path('missions/<int:pk>/view/', views.MissionDetailView.as_view(), name='mission_detail'),


]

 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
