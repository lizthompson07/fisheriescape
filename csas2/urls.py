from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # settings


    path('settings/document-types/', views.DocumentTypeFormsetView.as_view(), name="manage_document_types"),
    path('settings/document-types/<int:pk>/delete/', views.DocumentTypeHardDeleteView.as_view(), name="delete_document_type"),
    path('settings/invitee-roles/', views.InviteeRoleFormsetView.as_view(), name="manage_invitee_roles"),
    path('settings/invitee-role/<int:pk>/delete/', views.InviteeRoleHardDeleteView.as_view(), name="delete_invitee_role"),
    # permissions
    path('settings/csas-admin-users/', views.CSASAdminUserFormsetView.as_view(), name="manage_csas_admin_users"),
    path('settings/csas-admin-user/<int:pk>/delete/', views.CSASAdminUserHardDeleteView.as_view(), name="delete_csas_admin_user"),
    # tags
    path('settings/tags/', views.TagFormsetView.as_view(), name="manage_tags"),
    path('settings/tag/<int:pk>/delete/', views.TagHardDeleteView.as_view(), name="delete_tag"),


    # people #
    ##########
    path('people/', views.PersonListView.as_view(), name="person_list"),  # TESTED
    path('people/new/', views.PersonCreateView.as_view(), name="person_new"),  # TESTED
    path('people/<int:pk>/view/', views.PersonDetailView.as_view(), name="person_detail"),  # TESTED
    path('people/<int:pk>/edit/', views.PersonUpdateView.as_view(), name="person_edit"),  # TESTED
    path('people/<int:pk>/delete/', views.PersonDeleteView.as_view(), name="person_delete"),  # TESTED

    # requests
    path('requests/', views.CSASRequestListView.as_view(), name="request_list"),
    path('requests/new/', views.CSASRequestCreateView.as_view(), name="request_new"),
    path('requests/<int:pk>/view/', views.CSASRequestDetailView.as_view(), name="request_detail"),
    path('requests/<int:pk>/edit/', views.CSASRequestUpdateView.as_view(), name="request_edit"),
    path('requests/<int:pk>/clone/', views.CSASRequestCloneUpdateView.as_view(), name="request_clone"),
    path('requests/<int:pk>/delete/', views.CSASRequestDeleteView.as_view(), name="request_delete"),
    path('requests/<int:pk>/submit/', views.CSASRequestSubmitView.as_view(), name="request_submit"),
    path('requests/print-requests/', views.CSASRequestPDFView.as_view(), name="request_pdf"),

    # request reviews
    path('request-reviews/', views.CSASRequestReviewTemplateView.as_view(), name="request_reviews"),

    # request files
    path('requests/<int:crequest>/new-file/', views.CSASRequestFileCreateView.as_view(), name='request_file_new'),
    path('request-files/<int:pk>/edit/', views.CSASRequestFileUpdateView.as_view(), name='request_file_edit'),
    path('request-files/<int:pk>/delete/', views.CSASRequestFileDeleteView.as_view(), name='request_file_delete'),

    # processes
    path('processes/', views.ProcessListView.as_view(), name="process_list"),
    path('processes/new/', views.ProcessCreateView.as_view(), name="process_new"),
    path('processes/<int:pk>/view/', views.ProcessDetailView.as_view(), name="process_detail"),
    path('processes/<int:pk>/edit/', views.ProcessUpdateView.as_view(), name="process_edit"),
    path('processes/<int:pk>/delete/', views.ProcessDeleteView.as_view(), name="process_delete"),
    path('processes/manage-postings/', views.ProcessPostingsVueJSView.as_view(), name="process_postings"),

    # request reviews
    path('process-reviews/', views.ProcessReviewTemplateView.as_view(), name="process_reviews"),

    # ToR
    path('processes/<int:process>/new-tor/', views.TermsOfReferenceCreateView.as_view(), name="tor_new"),
    path('terms-of-reference/<int:pk>/edit/', views.TermsOfReferenceUpdateView.as_view(), name="tor_edit"),
    path('terms-of-reference/<int:pk>/delete/', views.TermsOfReferenceDeleteView.as_view(), name="tor_delete"),
    path('terms-of-reference/<int:pk>/export/', views.tor_export, name="tor_export"),
    path('terms-of-reference/<int:pk>/html/', views.TermsOfReferenceHTMLDetailView.as_view(), name="tor_html"),

    # meetings
    path('meetings/', views.MeetingListView.as_view(), name="meeting_list"),
    path('processes/<int:process>/new-meeting/', views.MeetingCreateView.as_view(), name="meeting_new"),
    path('meetings/<int:pk>/view/', views.MeetingDetailView.as_view(), name="meeting_detail"),
    path('meetings/<int:pk>/edit/', views.MeetingUpdateView.as_view(), name="meeting_edit"),
    path('meetings/<int:pk>/delete/', views.MeetingDeleteView.as_view(), name="meeting_delete"),

    # meeting files
    path('meetings/<int:meeting>/new-file/', views.MeetingFileCreateView.as_view(), name='meeting_file_new'),
    path('meeting-files/<int:pk>/edit/', views.MeetingFileUpdateView.as_view(), name='meeting_file_edit'),
    path('meeting-files/<int:pk>/delete/', views.MeetingFileDeleteView.as_view(), name='meeting_file_delete'),

    # docs
    path('documents/', views.DocumentListView.as_view(), name="document_list"),
    path('processes/<int:process>/new-document/', views.DocumentCreateView.as_view(), name="document_new"),
    path('doc-new/', views.DocumentCreateView.as_view(), name="document_new"),
    path('documents/<int:pk>/view/', views.DocumentDetailView.as_view(), name="document_detail"),
    path('documents/<int:pk>/edit/', views.DocumentUpdateView.as_view(), name="document_edit"),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name="document_delete"),

    # to-do
    path('my-todo-list/', views.ToDoListTemplateView.as_view(), name="todo_list"),

    # reports
    path('reports/', views.ReportSearchFormView.as_view(), name="reports"),
    path('reports/meeting/', views.meeting_report, name="meeting_report"),
    path('reports/requests/', views.request_list_report, name="request_list_report"),
    path('reports/processes/', views.process_list_report, name="process_list_report"),

]

app_name = 'csas2'
