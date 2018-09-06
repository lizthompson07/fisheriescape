from django.urls import path
from . import views

app_name = 'herring'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),
    path('', views.IndexView.as_view(), name ="index" ),

    # SAMPLES #
    ###########

    path('samples/port/new/', views.PortSampleCreateView.as_view(), name ="port_sample_new"),
    path('samples/port/<int:pk>/detail/', views.PortSampleDetailView.as_view(), name ="port_sample_detail"),
    path('samples/port/<int:pk>/edit/', views.PortSampleUpdateView.as_view(), name ="port_sample_edit"),




]
