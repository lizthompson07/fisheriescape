from django.urls import path
from . import views

app_name = 'ihub'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),

    # PERSON #
    ##########
    path('people/', views.PersonListView.as_view(), name="person_list"),
    path('person/new/', views.PersonCreateView.as_view(), name="person_new"),
    path('person/new/popout/', views.PersonCreateViewPopout.as_view(), name="person_new_pop"),
    path('person/<int:pk>/view/', views.PersonDetailView.as_view(), name="person_detail"),
    path('person/<int:pk>/edit/', views.PersonUpdateView.as_view(), name="person_edit"),
    path('person/<int:pk>/edit/popout/', views.PersonUpdateViewPopout.as_view(), name="person_edit_pop"),
    path('person/<int:pk>/delete/', views.PersonDeleteView.as_view(), name="person_delete"),

    # ORGANIZATION #
    ################
    path('organizations/', views.OrganizationListView.as_view(), name="org_list"),
    path('organization/new/', views.OrganizationCreateView.as_view(), name="org_new"),
    path('organization/<int:pk>/view/', views.OrganizationDetailView.as_view(), name="org_detail"),
    path('organization/<int:pk>/edit/', views.OrganizationUpdateView.as_view(), name="org_edit"),
    path('organization/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name="org_delete"),

    # ORGANIZATIONPERSON #
    ######################
    path('organization/<int:org>/member/new/', views.MemberCreateView.as_view(), name="member_new"),
    path('member/<int:pk>/edit/', views.MemberUpdateView.as_view(), name="member_edit"),
    path('member/<int:pk>/delete/', views.member_delete, name="member_delete"),

    # # Entry #
    # #########
    path('entries/', views.EntryListView.as_view(), name="entry_list"),
    path('entry/new/', views.EntryCreateView.as_view(), name="entry_new"),
    path('entry/<int:pk>/view', views.EntryDetailView.as_view(), name="entry_detail"),
    path('entry/<int:pk>/edit', views.EntryUpdateView.as_view(), name="entry_edit"),
    path('entry/<int:pk>/delete', views.EntryDeleteView.as_view(), name="entry_delete"),

    # NOTES #
    #########
    path('entry/<int:entry>/note/new/', views.NoteCreateView.as_view(), name="note_new"),
    path('note/<int:pk>/edit/', views.NoteUpdateView.as_view(), name="note_edit"),
    path('note/<int:pk>/delete/', views.note_delete, name="note_delete"),

    # ENTRYPERSON #
    ###############
    path('entry/<int:entry>/person/new/', views.EntryPersonCreateView.as_view(), name="ep_new"),
    path('dfo-person/<int:pk>/edit/', views.EntryPersonUpdateView.as_view(), name="ep_edit"),
    path('dfo-person/<int:pk>/delete/', views.entry_person_delete, name="ep_delete"),

    # FILE #
    ########
    path('entry/<int:entry>/file/new/', views.FileCreateView.as_view(), name="file_new"),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name="file_edit"),
    path('file/<int:pk>/delete/', views.file_delete, name="file_delete"),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/capacity-report/fy/<str:fy>/orgs/<str:orgs>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    path('reports/capacity-report/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    path('reports/capacity-report/fy/<str:fy>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    path('reports/capacity-report/orgs/<str:orgs>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),

    # SETTINGS #
    ############
    path('settings/sectors/', views.manage_sectors, name="manage_sectors"),
    path('settings/member-roles/', views.manage_roles, name="manage_roles"),
    path('settings/organizations/', views.manage_orgs, name="manage_orgs"),

]
