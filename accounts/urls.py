from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    # path('login/', views.UserLoginView.as_view(), name='login'),
    path('denied/', views.access_denied, name='denied_access'),
    path('denied/custodians-only/', views.access_denied_custodian, name='denied_access_custodian'),
    path('denied/adm-admin-only/', views.access_denied_adm, name='denied_access_adm'),
    path('denied/project-leads-only/', views.access_denied_project_leads_only, name='denied_project_leads_only'),
    path('denied/section-heads-only/', views.access_denied_section_heads_only, name='denied_section_heads_only'),
    path('denied/section-heads-only/', views.access_denied_manager_or_admin_only, name='denied_manager_or_admin_only'),
    path('denied/scifi/', views.access_denied_scifi, name='denied_access_scifi'),


    path('login', views.sign_in, name='login'),
    path('callback', views.callback, name='callback'),

    path('signup/', views.signup, name='signup'),
    path('activate/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('resend-verification-email/<str:email>', views.resend_verification_email, name='resend_verification_email'),
    path('verified/', views.account_verified, name='verified'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='account'),
    path('profiles/<int:pk>/edit/', views.ProfileUpdateView.as_view(), name='profile'),
    path('users/change-password/', views.change_password, name='change_password'),
    path('account-request/', views.account_request, name='account_request'),
    path('login_required/', views.UserLoginRequiredView.as_view()),
    path('request-access/', views.RequestAccessFormView.as_view(), name='request_access')

    ### NOTE: Password reset views are mapped in the dm_apps urls.py file. Views are still in the Accounts app views.py

]
