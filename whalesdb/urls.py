from django.urls import path
from . import views

app_name = 'whalesdb'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),

    # Specialized EQH hydrophone forms
    path('create/eqh', views.CreateHydrophone.as_view(), name="create_eqh"),
    path('details/<int:pk>/eqh', views.DetailsHydrophone.as_view(), name="details_eqh"),
    path('list/eqh', views.ListHydrophone.as_view(), name="list_eqh"),

    # Sepcialized EQR recorder forms
    path('create/eqr', views.CreateRecorder.as_view(), name="create_eqr"),
    path('details/<int:pk>/recorder', views.DetailsRecorder.as_view(), name="details_eqr"),
    path('list/eqr', views.ListRecorder.as_view(), name="list_eqr"),

    # Used in the details page for EQH hydrophones and EQR Recorders
    path('create/parameter/<str:pop>/<int:emm_id>/', views.CreateParameter.as_view(), name="create_parameter"),
    path('delete/parameter/<str:url>/<int:emm_id>/<int:prm_id>/', views.par_delete, name="delete_parameter"),

    # Used in the details page for EQR Recorders
    path('create/channel/<str:pop>/<int:emm_id>/',  views.CreateChannel.as_view(), name="create_channel"),
    path('delete/channel/<int:ecp_id>/', views.ecp_delete, name="delete_channel"),

    # If no specalized form is found the generic smart forms will be used
    path('create/<str:obj_name>', views.CreateSmartForm.as_view(), name="create_obj"),
    path('update/<str:obj_name>/<int:pk>', views.UpdateSmartForm.as_view(), name="create_obj"),
    path('list/<str:obj_name>', views.ListSmart.as_view(), name="list_obj"),

    # Specialized STE Station Event Code form
    path('set/edit', views.SetCodeEditView.as_view(), name="ste"),

    # Specialized TEA Team Event code form
    path('team/edit', views.TeaCodeEditView.as_view(), name="tea"),

    # Specialized RTT Time Zone code form
    path('rtt/edit', views.RttCodeEditView.as_view(), name="rtt"),

    # If no specalized form is found for codelists the generic code entry/list forms will be used
    path('<str:lookup>/edit', views.CodeEditView.as_view(), name="code_entry"),
    path('<str:lookup>/list', views.CodeListView.as_view(), name="code_list"),

]