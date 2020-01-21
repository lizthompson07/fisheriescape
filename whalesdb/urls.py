from django.urls import path
from . import views

app_name = 'whalesdb'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),

    path('create/stn', views.CreateStn.as_view(), name="create_stn"),
    path('details/<int:pk>/stn', views.DetailsStn.as_view(), name="details_stn"),
    path('list/stn/', views.ListStn.as_view(), name="list_stn"),

    path('create/prj', views.CreatePrj.as_view(), name="create_prj"),
    path('details/<int:pk>/prj', views.DetailsPrj.as_view(), name="details_prj"),
    path('list/prj/', views.ListPrj.as_view(), name="list_prj"),

    # General EMM Make and Model forms
    path('create/emm', views.CreateMakeModel.as_view(), name="create_emm"),
    path('details/<int:pk>/emm', views.DetailsMakeModel.as_view(), name="details_emm"),
    path('list/emm', views.ListMakeModel.as_view(), name="list_emm"),

    # Specialized EQH hydrophone forms
    path('create/eqh', views.CreateHydrophone.as_view(), name="create_eqh"),
    path('details/<int:pk>/eqh', views.DetailsHydrophone.as_view(), name="details_eqh"),
    path('list/eqh', views.ListHydrophone.as_view(), name="list_eqh"),

    # Sepcialized EQR recorder forms
    path('create/eqr', views.CreateRecorder.as_view(), name="create_eqr"),
    path('details/<int:pk>/recorder', views.DetailsRecorder.as_view(), name="details_eqr"),
    path('list/eqr', views.ListRecorder.as_view(), name="list_eqr"),

    # Sepcialized DEP Deploymnet forms
    path('create/dep', views.CreateDeployment.as_view(), name="create_dep"),
    path('update/dep/<int:pk>', views.UpdateDeployment.as_view(), name="update_dep"),

    # Used in the details page for EQH hydrophones and EQR Recorders
    path('create/prm/<str:pop>/<int:emm_id>/', views.CreatePrmParameter.as_view(), name="create_parameter"),
    path('delete/prm/<str:url>/<int:emm_id>/<int:prm_id>/', views.par_delete, name="delete_parameter"),

    # Used in the details page for EQR Recorders
    path('create/channel/<str:pop>/<int:emm_id>/',  views.CreateChannel.as_view(), name="create_channel"),
    path('delete/channel/<int:ecp_id>/', views.ecp_delete, name="delete_channel"),

    # If no specalized form is found the generic smart forms will be used
    path('create/<str:obj_name>', views.CreateSmartForm.as_view(), name="create_obj"),
    path('create/<str:obj_name>/<str:pop>', views.CreateSmartForm.as_view(), name="create_obj"),
    path('update/<str:obj_name>/<int:pk>', views.UpdateSmartForm.as_view(), name="create_obj"),
    path('list/<str:obj_name>', views.ListSmart.as_view(), name="list_obj"),

    # Specialized STE Station Event Code form
    path('set/edit', views.SetCodeEditView.as_view(), name="set"),

    # Specialized TEA Team Event code form
    path('team/edit', views.TeaCodeEditView.as_view(), name="tea"),

    # Specialized RTT Time Zone code form
    path('rtt/edit', views.RttCodeEditView.as_view(), name="rtt"),

    # Specialized PRM Parameter code form
    path('prm/edit', views.PrmCodeEditView.as_view(), name="prm"),

    # Specialized ADC Bits code form
    path('eqa/edit', views.EqaCodeEditView.as_view(), name="eqa"),

    # Specialized EQT Equipment Type code form
    path('eqt/edit', views.EqtCodeEditView.as_view(), name="eqt"),

    # If no specalized form is found for codelists the generic code entry/list forms will be used
    path('<str:lookup>/list', views.CodeListView.as_view(), name="code_list"),

]
