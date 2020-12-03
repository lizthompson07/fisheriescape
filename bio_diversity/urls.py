from django.urls import path
from . import views

app_name = 'bio_diversity'

urlpatterns = [
    # for home/index page
    path('', views.IndexTemplateView.as_view(),    name="index"),

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

    path('create/unit/', views.UnitCreate.as_view(), name="create_unit"),
    path('details/unit/<int:pk>/', views.UnitDetails.as_view(), name="details_unit"),
    path('list/unit/', views.UnitList.as_view(), name="list_unit"),
    path('update/unit/<int:pk>/', views.UnitUpdate.as_view(), name="update_unit"),

]
