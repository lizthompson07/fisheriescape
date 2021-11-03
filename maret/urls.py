from django.urls import path
from . import views, utils

app_name = 'maret'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('organization/', views.OrganizationListView.as_view(), name="org_list"),
    path('organization/new/', views.OrganizationCreateView.as_view(), name="org_new"),
    path('organization/<int:pk>/view/', views.OrganizationDetailView.as_view(), name="org_detail"),
    path('organization/<int:pk>/edit/', views.OrganizationUpdateView.as_view(), name="org_edit"),
    path('organization/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name="org_delete"),

    # PERSON #
    ##########
    path('person/', views.PersonListView.as_view(), name="person_list"),
    path('person/new/', views.PersonCreateView.as_view(), name="person_new"),
    path('person/new/popout/', views.PersonCreateViewPopout.as_view(), name="person_new_pop"),
    path('person/<int:pk>/view/', views.PersonDetailView.as_view(), name="person_detail"),
    path('person/<int:pk>/edit/', views.PersonUpdateView.as_view(), name="person_edit"),
    path('person/<int:pk>/edit/popout/', views.PersonUpdateViewPopout.as_view(), name="person_edit_pop"),
    path('person/<int:pk>/delete/', views.PersonDeleteView.as_view(), name="person_delete"),

    # ORGANIZATIONPERSON #
    ######################
    path('organization/<int:org>/member/new/', views.MemberCreateView.as_view(), name="member_new"),
    path('member/<int:pk>/edit/', views.MemberUpdateView.as_view(), name="member_edit"),
    path('member/<int:pk>/delete/', views.MemberDeleteView.as_view(), name="member_delete"),

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
    path('manage/areas/', views.AreaFormsetView.as_view(), name="manage_areas"),

    path('ajax/get_divisions/', utils.ajax_get_divisions, name='ajax_get_divisions'),
]


