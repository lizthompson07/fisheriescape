from django.urls import path
from . import views

app_name = 'maret'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('list/entry', views.EntryListView.as_view(), name="entry_list"),
    path('list/organization', views.OrganizationListView.as_view(), name="org_list"),
    path('list/person', views.PersonListView.as_view(), name="person_list")
]

