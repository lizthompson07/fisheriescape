from django.urls import path
from . import views

app_name = 'spot'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),
    #
    # # PERSON #
    # ##########
    # path('people/', views.PersonListView.as_view(), name="person_list"),
    # path('person/new/', views.PersonCreateView.as_view(), name="person_new"),
    # path('person/new/popout/', views.PersonCreateViewPopout.as_view(), name="person_new_pop"),
    # path('person/<int:pk>/view/', views.PersonDetailView.as_view(), name="person_detail"),
    # path('person/<int:pk>/edit/', views.PersonUpdateView.as_view(), name="person_edit"),
    # path('person/<int:pk>/edit/popout/', views.PersonUpdateViewPopout.as_view(), name="person_edit_pop"),
    # path('person/<int:pk>/delete/', views.PersonDeleteView.as_view(), name="person_delete"),
    #
    # ORGANIZATION #
    ################
    path('organizations/', views.OrganizationListView.as_view(), name="org_list"),
    path('organization/new/', views.OrganizationCreateView.as_view(), name="org_new"),
    path('organization/<int:pk>/view/', views.OrganizationDetailView.as_view(), name="org_detail"),
    path('organization/<int:pk>/edit/', views.OrganizationUpdateView.as_view(), name="org_edit"),
    path('organization/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name="org_delete"),

    # ORGANIZATION MEMBER #
    ######################
    path('organization/<int:org>/member/new/', views.MemberCreateView.as_view(), name="member_new"),
    path('member/<int:pk>/edit/', views.MemberUpdateView.as_view(), name="member_edit"),
    path('member/<int:pk>/delete/', views.member_delete, name="member_delete"),

    # # RECIPIENTS #
    # ##############
    # path('instructions/<int:instruction>/member/<int:member>/add/', views.RecipientCreateView.as_view(), name="recipient_new"),
    # path('recipient/<int:pk>/edit/', views.RecipientUpdateView.as_view(), name="recipient_edit"),
    # path('recipient/<int:pk>/delete/', views.recipient_delete, name="recipient_delete"),
    #
    # # Reports #
    # ###########
    # path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    # path('reports/export-custom-list/<str:provinces>/<str:groupings>/<str:sectors>/<str:regions>/<int:is_indigenous>/<str:species>', views.export_custom_list, name="export_custom_list"),



]
