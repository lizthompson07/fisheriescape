from django.urls import path
from . import views

app_name = 'whalesdb'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),

    path('<str:lookup>/edit', views.CodeEditView.as_view(), name="code_entry"),
    path('<str:lookup>/list', views.CodeListView.as_view(), name="code_list"),

    path('makemodel', views.CreateMakeModel.as_view(), name="create_makemodel"),
    path('hydrophone', views.CreateHydrophone.as_view(), name="create_hydrophone"),

    path('list/hydrophone', views.ListViewHydrophone.as_view(), name="list_hydrophone"),
]