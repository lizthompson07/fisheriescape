from django.urls import path
from . import views

app_name = 'whalesdb'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    # CRUISES #
    ###########
    path('list/cru/', views.CruList.as_view(), name="list_cru"),
    path('create/cru/', views.CruCreate.as_view(), name="create_cru"),
    path('details/cru/<int:pk>/', views.CruDetails.as_view(), name="details_cru"),
    path('update/cru/<int:pk>/', views.CruUpdate.as_view(), name="update_cru"),
    path('delete/cru/<int:pk>/', views.CruDeleteView.as_view(), name="delete_cru"),

    path('create/dep/', views.DepCreate.as_view(), name="create_dep"),
    path('create/dep/<str:pop>/', views.DepCreate.as_view(), name="create_dep"),
    path('update/dep/<int:pk>/', views.DepUpdate.as_view(), name="update_dep"),
    path('update/dep/<int:pk>/<str:pop>/', views.DepUpdate.as_view(), name="update_dep"),
    path('details/dep/<int:pk>/', views.DepDetails.as_view(), name="details_dep"),
    path('list/dep/', views.DepList.as_view(), name="list_dep"),

    path('create/eda/<int:dep>/<str:pop>/', views.EdaCreate.as_view(), name="create_eda"),

    path('create/emm/', views.EmmCreate.as_view(), name="create_emm"),
    path('create/emm/<str:pop>/', views.EmmCreate.as_view(), name="create_emm"),
    path('update/emm/<int:pk>/', views.EmmUpdate.as_view(), name="update_emm"),
    path('details/emm/<int:pk>/', views.EmmDetails.as_view(), name="details_emm"),
    path('list/emm/', views.EmmList.as_view(), name="list_emm"),

    path('create/eqh/<int:pk>/<str:pop>/', views.EqhCreate.as_view(), name="create_eqh"),
    path('update/eqh/<int:pk>/<str:pop>/', views.EqhUpdate.as_view(), name="update_eqh"),

    path('create/eqo/<str:pop>/', views.EqoCreate.as_view(), name="create_eqo"),

    path('create/eqp/', views.EqpCreate.as_view(), name="create_eqp"),
    path('update/eqp/<int:pk>/', views.EqpUpdate.as_view(), name="update_eqp"),
    path('update/eqp/<int:pk>/<str:pop>/', views.EqpUpdate.as_view(), name="update_eqp"),
    path('details/eqp/<int:pk>/', views.EqpDetails.as_view(), name="details_eqp"),
    path('list/eqp/', views.EqpList.as_view(), name="list_eqp"),

    path('create/eqr/<int:pk>/<str:pop>/', views.EqrCreate.as_view(), name="create_eqr"),
    path('update/eqr/<int:pk>/<str:pop>/', views.EqrUpdate.as_view(), name="update_eqr"),

    path('list/etr/', views.EtrList.as_view(), name="list_etr"),
    path('create/etr/', views.EtrCreate.as_view(), name="create_etr"),
    path('details/etr/<int:pk>/', views.EtrDetails.as_view(), name="details_etr"),
    path('update/etr/<int:pk>/', views.EtrUpdate.as_view(), name="update_etr"),
    path('update/etr/<int:pk>/<str:pop>/', views.EtrUpdate.as_view(), name="update_etr"),

    path('create/mor/', views.MorCreate.as_view(), name="create_mor"),
    path('create/mor/<str:pop>/', views.MorCreate.as_view(), name="create_mor"),
    path('update/mor/<int:pk>/', views.MorUpdate.as_view(), name="update_mor"),
    path('update/mor/<int:pk>/<str:pop>/', views.MorUpdate.as_view(), name="update_mor"),
    path('details/mor/<int:pk>/', views.MorDetails.as_view(), name="details_mor"),
    path('list/mor/', views.MorList.as_view(), name="list_mor"),

    path('create/prj/', views.PrjCreate.as_view(), name="create_prj"),
    path('create/prj/<str:pop>/', views.PrjCreate.as_view(), name="create_prj"),
    path('update/prj/<int:pk>/', views.PrjUpdate.as_view(), name="update_prj"),
    path('update/prj/<int:pk>/<str:pop>/', views.PrjUpdate.as_view(), name="update_prj"),
    path('details/prj/<int:pk>/', views.PrjDetails.as_view(), name="details_prj"),
    path('list/prj/', views.PrjList.as_view(), name="list_prj"),

    path('create/rsc/', views.RscCreate.as_view(), name="create_rsc"),
    path('details/rsc/<int:pk>/', views.RscDetails.as_view(), name="details_rsc"),
    path('list/rsc/', views.RscList.as_view(), name="list_rsc"),

    path('create/rst/<int:rsc>/<str:pop>/', views.RstCreate.as_view(), name="create_rst"),
    path('delete/rst/<int:pk>/', views.rst_delete, name="delete_rst"),

    path('create/ste/<int:dep_id>/<int:pk>/<str:pop>/', views.SteCreate.as_view(), name="create_ste"),
    path('update/ste/<int:dep_id>/<int:pk>/<str:pop>/', views.SteUpdate.as_view(), name="update_ste"),

    path('create/stn/', views.StnCreate.as_view(), name="create_stn"),
    path('create/stn/<str:pop>/', views.StnCreate.as_view(), name="create_stn"),
    path('update/stn/<int:pk>/', views.StnUpdate.as_view(), name="update_stn"),
    path('update/stn/<int:pk>/<str:pop>/', views.StnUpdate.as_view(), name="update_stn"),
    path('details/stn/<int:pk>/', views.StnDetails.as_view(), name="details_stn"),
    path('list/stn/', views.StnList.as_view(), name="list_stn"),

    path('create/tea/', views.TeaCreate.as_view(), name="create_tea"),
    path('list/tea/', views.TeaList.as_view(), name="list_tea"),

    path('create/rtt/', views.RttCreate.as_view(), name="create_rtt"),
    path('list/rtt/', views.RttList.as_view(), name="list_rtt"),
    path('details/rtt/<int:pk>/', views.RttDetails.as_view(), name="details_rtt"),

    path('create/rec/', views.RecCreate.as_view(), name="create_rec"),
    path('list/rec/', views.RecList.as_view(), name="list_rec"),
    path('details/rec/<int:pk>/', views.RecDetails.as_view(), name="details_rec"),
    path('update/rec/<int:pk>/', views.RecUpdate.as_view(), name="update_rec"),

    path('create/ret/', views.RetCreate.as_view(), name="create_ret"),
    path('list/ret/', views.RetList.as_view(), name="list_ret"),
    path('update/ret/<int:pk>/', views.RetUpdate.as_view(), name="update_ret"),
    path('delete/ret/<int:pk>/', views.ret_delete, name="delete_ret"),

    path('create/rci/<int:rec_id>/<str:pop>/', views.RciCreate.as_view(), name="create_rci"),

    path('create/ree/<int:rec_id>/<str:pop>/', views.ReeCreate.as_view(), name="create_ree"),
]

