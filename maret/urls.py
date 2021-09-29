from django.urls import path
from . import views

app_name = 'maret'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('organization/', views.OrganizationListView.as_view(), name="org_list"),
    path('organization/new/', views.OrganizationCreateView.as_view(), name="org_new"),
    path('organization/<int:pk>/view/', views.OrganizationDetailView.as_view(), name="org_detail"),

    path('person/', views.PersonListView.as_view(), name="person_list"),

    path('interaction/', views.InteractionListView.as_view(), name="interaction_list"),
    path('interaction/new/', views.InteractionCreateView.as_view(), name="interaction_new"),
    path('interaction/<int:pk>/view/', views.InteractionDetailView.as_view(), name="interaction_detail"),
    path('interaction/<int:pk>/edit/', views.InteractionUpdateView.as_view(), name="interaction_edit"),
    path('interaction/<int:pk>/delete/', views.InteractionDeleteView.as_view(), name="interaction_delete"),

    path('committee/', views.CommitteeListView.as_view(), name="committee_list"),
    path('committee/new/', views.CommitteeCreateView.as_view(), name="committee_new"),
    path('committee/<int:pk>/view/', views.CommitteeDetailView.as_view(), name="committee_detail"),
    path('committee/<int:pk>/edit/', views.CommitteeUpdateView.as_view(), name="committee_edit"),
    path('committee/<int:pk>/delete/', views.CommitteeDeleteView.as_view(), name="committee_delete"),

    path('manage/topics/', views.TopicFormsetView.as_view(), name="manage_topics"),
    path('manage/species/', views.SpeciesFormsetView.as_view(), name="manage_species"),
]


