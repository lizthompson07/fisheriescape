from django.urls import path
from . import views

app_name = 'bio_diversity'

urlpatterns = [
    # for home/index page
    path('', views.IndexTemplateView.as_view(),    name="index"),

    path('create/contdc/', views.ContdcCreate.as_view(), name="create_contdc"),
    path('details/contdc/<int:pk>/', views.ContdcDetails.as_view(), name="details_contdc"),
    path('list/contdc/', views.ContdcList.as_view(), name="list_contdc"),
    path('update/contdc/<int:pk>/', views.ContdcUpdate.as_view(), name="update_contdc"),

    path('create/cdsc/', views.CdscCreate.as_view(), name="create_cdsc"),
    path('details/cdsc/<int:pk>/', views.CdscDetails.as_view(), name="details_cdsc"),
    path('list/cdsc/', views.CdscList.as_view(), name="list_cdsc"),
    path('update/cdsc/<int:pk>/', views.CdscUpdate.as_view(), name="update_cdsc"),

    path('create/cup/', views.CupCreate.as_view(), name="create_cup"),
    path('details/cup/<int:pk>/', views.CupDetails.as_view(), name="details_cup"),
    path('list/cup/', views.CupList.as_view(), name="list_cup"),
    path('update/cup/<int:pk>/', views.CupUpdate.as_view(), name="update_cup"),
    
    path('create/cupd/', views.CupdCreate.as_view(), name="create_cupd"),
    path('details/cupd/<int:pk>/', views.CupdDetails.as_view(), name="details_cupd"),
    path('list/cupd/', views.CupdList.as_view(), name="list_cupd"),
    path('update/cupd/<int:pk>/', views.CupdUpdate.as_view(), name="update_cupd"),
    
    path('create/heat/', views.HeatCreate.as_view(), name="create_heat"),
    path('details/heat/<int:pk>/', views.HeatDetails.as_view(), name="details_heat"),
    path('list/heat/', views.HeatList.as_view(), name="list_heat"),
    path('update/heat/<int:pk>/', views.HeatUpdate.as_view(), name="update_heat"),
    
    path('create/heatd/', views.HeatdCreate.as_view(), name="create_heatd"),
    path('details/heatd/<int:pk>/', views.HeatdDetails.as_view(), name="details_heatd"),
    path('list/heatd/', views.HeatdList.as_view(), name="list_heatd"),
    path('update/heatd/<int:pk>/', views.HeatdUpdate.as_view(), name="update_heatd"),
    
    path('create/inst/', views.InstCreate.as_view(), name="create_inst"),
    path('details/inst/<int:pk>/', views.InstDetails.as_view(), name="details_inst"),
    path('list/inst/', views.InstList.as_view(), name="list_inst"),
    path('update/inst/<int:pk>/', views.InstUpdate.as_view(), name="update_inst"),

    path('create/instc/', views.InstcCreate.as_view(), name="create_instc"),
    path('details/instc/<int:pk>/', views.InstcDetails.as_view(), name="details_instc"),
    path('list/instc/', views.InstcList.as_view(), name="list_instc"),
    path('update/instc/<int:pk>/', views.InstcUpdate.as_view(), name="update_instc"),

    path('create/instd/', views.InstdCreate.as_view(), name="create_instd"),
    path('details/instd/<int:pk>/', views.InstdDetails.as_view(), name="details_instd"),
    path('list/instd/', views.InstdList.as_view(), name="list_instd"),
    path('update/instd/<int:pk>/', views.InstdUpdate.as_view(), name="update_instd"),

    path('create/instdc/', views.InstdcCreate.as_view(), name="create_instdc"),
    path('details/instdc/<int:pk>/', views.InstdcDetails.as_view(), name="details_instdc"),
    path('list/instdc/', views.InstdcList.as_view(), name="list_instdc"),
    path('update/instdc/<int:pk>/', views.InstdcUpdate.as_view(), name="update_instdc"),

    path('create/orga/', views.OrgaCreate.as_view(), name="create_orga"),
    path('details/orga/<int:pk>/', views.OrgaDetails.as_view(), name="details_orga"),
    path('list/orga/', views.OrgaList.as_view(), name="list_orga"),
    path('update/orga/<int:pk>/', views.OrgaUpdate.as_view(), name="update_orga"),

    path('create/prog/', views.ProgCreate.as_view(), name="create_prog"),
    path('details/prog/<int:pk>/', views.ProgDetails.as_view(), name="details_prog"),
    path('list/prog/', views.ProgList.as_view(), name="list_prog"),
    path('update/prog/<int:pk>/', views.ProgUpdate.as_view(), name="update_prog"),

    path('create/proga/', views.ProgaCreate.as_view(), name="create_proga"),
    path('details/proga/<int:pk>/', views.ProgaDetails.as_view(), name="details_proga"),
    path('list/proga/', views.ProgaList.as_view(), name="list_proga"),
    path('update/proga/<int:pk>/', views.ProgaUpdate.as_view(), name="update_proga"),

    path('create/prot/', views.ProtCreate.as_view(), name="create_prot"),
    path('details/prot/<int:pk>/', views.ProtDetails.as_view(), name="details_prot"),
    path('list/prot/', views.ProtList.as_view(), name="list_prot"),
    path('update/prot/<int:pk>/', views.ProtUpdate.as_view(), name="update_prot"),

    path('create/protc/', views.ProtcCreate.as_view(), name="create_protc"),
    path('details/protc/<int:pk>/', views.ProtcDetails.as_view(), name="details_protc"),
    path('list/protc/', views.ProtcList.as_view(), name="list_protc"),
    path('update/protc/<int:pk>/', views.ProtcUpdate.as_view(), name="update_protc"),

    path('create/protf/', views.ProtfCreate.as_view(), name="create_protf"),
    path('details/protf/<int:pk>/', views.ProtfDetails.as_view(), name="details_protf"),
    path('list/protf/', views.ProtfList.as_view(), name="list_protf"),
    path('update/protf/<int:pk>/', views.ProtfUpdate.as_view(), name="update_protf"),

    path('create/tank/', views.TankCreate.as_view(), name="create_tank"),
    path('details/tank/<int:pk>/', views.TankDetails.as_view(), name="details_tank"),
    path('list/tank/', views.TankList.as_view(), name="list_tank"),
    path('update/tank/<int:pk>/', views.TankUpdate.as_view(), name="update_tank"),

    path('create/tankd/', views.TankdCreate.as_view(), name="create_tankd"),
    path('details/tankd/<int:pk>/', views.TankdDetails.as_view(), name="details_tankd"),
    path('list/tankd/', views.TankdList.as_view(), name="list_tankd"),
    path('update/tankd/<int:pk>/', views.TankdUpdate.as_view(), name="update_tankd"),

    path('create/tray/', views.TrayCreate.as_view(), name="create_tray"),
    path('details/tray/<int:pk>/', views.TrayDetails.as_view(), name="details_tray"),
    path('list/tray/', views.TrayList.as_view(), name="list_tray"),
    path('update/tray/<int:pk>/', views.TrayUpdate.as_view(), name="update_tray"),
    
    path('create/trayd/', views.TraydCreate.as_view(), name="create_trayd"),
    path('details/trayd/<int:pk>/', views.TraydDetails.as_view(), name="details_trayd"),
    path('list/trayd/', views.TraydList.as_view(), name="list_trayd"),
    path('update/trayd/<int:pk>/', views.TraydUpdate.as_view(), name="update_trayd"),

    path('create/trof/', views.TrofCreate.as_view(), name="create_trof"),
    path('details/trof/<int:pk>/', views.TrofDetails.as_view(), name="details_trof"),
    path('list/trof/', views.TrofList.as_view(), name="list_trof"),
    path('update/trof/<int:pk>/', views.TrofUpdate.as_view(), name="update_trof"),
    
    path('create/trofd/', views.TrofdCreate.as_view(), name="create_trofd"),
    path('details/trofd/<int:pk>/', views.TrofdDetails.as_view(), name="details_trofd"),
    path('list/trofd/', views.TrofdList.as_view(), name="list_trofd"),
    path('update/trofd/<int:pk>/', views.TrofdUpdate.as_view(), name="update_trofd"),
    
    path('create/unit/', views.UnitCreate.as_view(), name="create_unit"),
    path('details/unit/<int:pk>/', views.UnitDetails.as_view(), name="details_unit"),
    path('list/unit/', views.UnitList.as_view(), name="list_unit"),
    path('update/unit/<int:pk>/', views.UnitUpdate.as_view(), name="update_unit"),

]
