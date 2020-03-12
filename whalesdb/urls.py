from django.urls import path
from . import views

app_name = 'whalesdb'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('create/dep/', views.CreateDep.as_view(), name="create_dep"),
    path('create/dep/<str:pop>/', views.CreateDep.as_view(), name="create_dep"),
    path('update/dep/<int:pk>/', views.UpdateDep.as_view(), name="update_dep"),
    path('update/dep/<int:pk>/<str:pop>/', views.UpdateDep.as_view(), name="update_dep"),
    path('details/dep/<int:pk>/', views.DetailsDep.as_view(), name="details_dep"),
    path('list/dep/', views.ListDep.as_view(), name="list_dep"),

    path('create/emm/', views.CreateEmm.as_view(), name="create_emm"),
    path('create/emm/<str:pop>/', views.CreateEmm.as_view(), name="create_emm"),
    path('update/emm/<int:pk>/<str:pop>/', views.UpdateEmm.as_view(), name="update_emm"),
    path('details/emm/<int:pk>/', views.DetailsEmm.as_view(), name="details_emm"),
    path('list/emm/', views.ListEmm.as_view(), name="list_emm"),

    path('create/eqh/<int:pk>/<str:pop>/', views.CreateEqh.as_view(), name="create_eqh"),
    path('update/eqh/<int:pk>/<str:pop>/', views.UpdateEqh.as_view(), name="update_eqh"),

    path('create/eqp/', views.CreateEqp.as_view(), name="create_eqp"),
    path('update/eqp/<int:pk>/', views.UpdateEqp.as_view(), name="update_eqp"),
    path('update/eqp/<int:pk>/<str:pop>/', views.UpdateEqp.as_view(), name="update_eqp"),
    path('details/eqp/<int:pk>/', views.DetailsEqp.as_view(), name="details_eqp"),
    path('list/eqp/', views.ListEqp.as_view(), name="list_eqp"),

    path('create/eqo/<str:pop>/', views.CreateEqo.as_view(), name="create_eqo"),

    path('create/mor/', views.CreateMor.as_view(), name="create_mor"),
    path('create/mor/<str:pop>/', views.CreateMor.as_view(), name="create_mor"),
    path('update/mor/<int:pk>/', views.UpdateMor.as_view(), name="update_mor"),
    path('update/mor/<int:pk>/<str:pop>/', views.UpdateMor.as_view(), name="update_mor"),
    path('details/mor/<int:pk>/', views.DetailsMor.as_view(), name="details_mor"),
    path('list/mor/', views.ListMor.as_view(), name="list_mor"),

    path('create/prj/', views.CreatePrj.as_view(), name="create_prj"),
    path('create/prj/<str:pop>/', views.CreatePrj.as_view(), name="create_prj"),
    path('update/prj/<int:pk>/', views.UpdatePrj.as_view(), name="update_prj"),
    path('update/prj/<int:pk>/<str:pop>/', views.UpdatePrj.as_view(), name="update_prj"),
    path('details/prj/<int:pk>/', views.DetailsPrj.as_view(), name="details_prj"),
    path('list/prj/', views.ListPrj.as_view(), name="list_prj"),

    path('create/ste/<int:dep_id>/<int:set_id>/<str:pop>/', views.CreateSte.as_view(), name="create_ste"),

    path('create/stn/', views.CreateStn.as_view(), name="create_stn"),
    path('create/stn/<str:pop>/', views.CreateStn.as_view(), name="create_stn"),
    path('update/stn/<int:pk>/', views.UpdateStn.as_view(), name="update_stn"),
    path('update/stn/<int:pk>/<str:pop>/', views.UpdateStn.as_view(), name="update_stn"),
    path('details/stn/<int:pk>/', views.DetailsStn.as_view(), name="details_stn"),
    path('list/stn/', views.ListStn.as_view(), name="list_stn"),
]
