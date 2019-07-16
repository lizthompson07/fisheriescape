from django.urls import path
from . import views

app_name = 'whalesdb'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),

    path('create/deployment', views.CreateDeploymentForm.as_view(), name="create_dep"),
    path('create/mooring', views.CreateMooringForm.as_view(), name="create_mor"),
    path('create/station', views.CreateStationForm.as_view(), name="create_stn"),
    path('create/project', views.CreateProjectForm.as_view(), name="create_prj"),
    path('create/cruise', views.CreateCruiseForm.as_view(), name="create_crs"),
    path('create/station_event', views.CreateStationEventForm.as_view(), name="create_ste"),

    path('create/record_event', views.CreateRecordEventForm.as_view(), name="create_rec"),
    path('create/record_schedule', views.CreateRecordScheduleForm.as_view(), name="create_rsc"),
    path('create/record_stage', views.CreateRecordStageForm.as_view(), name="create_rst"),
    path('create/team', views.CreateTeamForm.as_view(), name="create_tea"),

    path('create/makemodel', views.CreateMakeModel.as_view(), name="create_makemodel"),
    path('create/hydrophone', views.CreateHydrophone.as_view(), name="create_hydrophone"),
    path('create/recorder', views.CreateRecorder.as_view(), name="create_recorder"),
    path('create/channel/<str:pop>/<int:eqr_id>/', views.CreateChannel.as_view(), name="create_channel"),

    path('details/<int:pk>/hydrophone', views.DetailsHydrophone.as_view(), name="details_hydrophone"),
    path('details/<int:pk>/recorder', views.DetailsRecorder.as_view(), name="details_recorder"),

    path('list/hydrophone', views.ListHydrophone.as_view(), name="list_hydrophone"),
    path('list/recorder', views.ListRecorder.as_view(), name="list_recorder"),

    path('<str:lookup>/edit', views.SetCodeEditView.as_view(), name="set_code_entry"),

    path('<str:lookup>/edit', views.CodeEditView.as_view(), name="code_entry"),
    path('<str:lookup>/list', views.CodeListView.as_view(), name="code_list"),

]