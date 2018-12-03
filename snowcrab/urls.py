from django.urls import path
from . import views

app_name = 'crab'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),

    # # CRUISE #
    # ##########
    # path('missions/', views.MissionYearListView.as_view(), name='mission_year_list'),
    # path('missions/<int:year>/list/', views.MissionListView.as_view(), name='mission_list'),
    # path('missions/<int:pk>/view/', views.MissionDetailView.as_view(), name='mission_detail'),
    # path('missions/<int:pk>/edit/', views.MissionUpdateView.as_view(), name='mission_edit'),
    # path('missions/<int:pk>/export-csv/', views.export_mission_csv, name='mission_export_csv'),
    #


]

 # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
