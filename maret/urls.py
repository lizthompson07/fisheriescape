from django.urls import path
from . import views

app_name = 'maret'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('list/interaction', views.InteractionListView.as_view(), name="interaction_list"),
    path('list/committee', views.CommitteeListView.as_view(), name="committee_list"),
    path('list/organization', views.OrganizationListView.as_view(), name="org_list"),
    path('list/person', views.PersonListView.as_view(), name="person_list"),

    path('new/interaction', views.InteractionCreateView.as_view(), name="interaction_new"),
    path('new/committee', views.CommitteeCreateView.as_view(), name="committee_new"),
    path('new/organization', views.OrganizationCreateView.as_view(), name="org_new"),

    path('manage/topics', views.TopicFormsetView.as_view(), name="manage_topics"),
    path('manage/species', views.SpeciesFormsetView.as_view(), name="manage_species"),
]


