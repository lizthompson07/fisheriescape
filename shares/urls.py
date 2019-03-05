from django.urls import path
from . import views

app_name = 'shares'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),
    path('email-list/', views.EmailListTemplateView.as_view(), name="email_list"),

    # SERVER #
    ##########
    path('servers/', views.ServerListView.as_view(), name="server_list"),
    path('server/new/', views.ServerCreateView.as_view(), name="server_new"),
    path('server/<int:pk>/view/', views.ServerDetailView.as_view(), name="server_detail"),
    path('server/<int:pk>/edit/', views.ServerUpdateView.as_view(), name="server_edit"),
    path('server/<int:pk>/delete/', views.ServerDeleteView.as_view(), name="server_delete"),

    # USER #
    ########
    path('users/', views.UserListView.as_view(), name="user_list"),
    path('user/new/', views.UserCreateView.as_view(), name="user_new"),
    path('user/<int:pk>/view/', views.UserDetailView.as_view(), name="user_detail"),
    path('user/<int:pk>/edit/', views.UserUpdateView.as_view(), name="user_edit"),
    path('user/<int:pk>/delete/', views.UserDeleteView.as_view(), name="user_delete"),
    path('user/<int:pk>/send-instructions/', views.send_instructions, name="send_instructions"),

    # SHARE #
    #########
    path('shares/', views.ShareListView.as_view(), name="share_list"),
    path('share/new/', views.ShareCreateView.as_view(), name="share_new"),
    path('share/<int:pk>/view/', views.ShareDetailView.as_view(), name="share_detail"),
    path('share/<int:pk>/edit/', views.ShareUpdateView.as_view(), name="share_edit"),
    path('share/<int:pk>/delete/', views.ShareDeleteView.as_view(), name="share_delete"),

    # # USER #
    # ########
    # path('users/', views.ServerListView.as_view(), name="server_list"),
    # path('user/new/', views.ServerCreateView.as_view(), name="server_new"),
    # path('user/<int:pk>/view/', views.ServerDetailView.as_view(), name="server_detail"),
    # path('user/<int:pk>/edit/', views.ServerUpdateView.as_view(), name="server_edit"),
    # path('user/<int:pk>/delete/', views.ServerDeleteView.as_view(), name="server_delete"),
    #
    # # ORGANIZATION #
    # ################
    # path('organizations/', views.OrganizationListView.as_view(), name="org_list"),
    # path('organization/new/', views.OrganizationCreateView.as_view(), name="org_new"),
    # path('organization/<int:pk>/view/', views.OrganizationDetailView.as_view(), name="org_detail"),
    # path('organization/<int:pk>/edit/', views.OrganizationUpdateView.as_view(), name="org_edit"),
    # path('organization/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name="org_delete"),
    #
    # # ORGANIZATION MEMBER #
    # ######################
    # path('organization/<int:org>/member/new/', views.MemberCreateView.as_view(), name="member_new"),
    # path('member/<int:pk>/edit/', views.MemberUpdateView.as_view(), name="member_edit"),
    # path('member/<int:pk>/delete/', views.member_delete, name="member_delete"),
    #
    # # Consultation Instructions #
    # #############################
    # path('organization/<int:org>/instructions/new/', views.InstructionCreateView.as_view(), name="instruction_new"),
    # path('instructions/<int:pk>/edit/', views.InstructionUpdateView.as_view(), name="instruction_edit"),
    # path('instructions/<int:pk>/delete/', views.InstructionDeleteView.as_view(), name="instruction_delete"),
    #
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
