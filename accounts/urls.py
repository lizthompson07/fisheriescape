from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('denied/', views.access_denied, name='denied_access'),
    path('denied/custodians-only/', views.access_denied_custodian, name='denied_access_custodian'),
    path('denied/scifi/', views.access_denied_scifi, name='denied_access_scifi'),

    path('signup/', views.signup, name='signup'),
    path('activate/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('resend-verification-email/<str:email>', views.resend_verification_email, name='resend_verification_email'),
    path('verified/', views.account_verified, name='verified'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='account'),
    path('users/change-password/', views.change_password, name='change_password'),
    path('account-request/', views.account_request, name='account_request'),
    path('login_required/', views.UserLoginRequiredView.as_view()),
    path('request-access/', views.RequestAccessFormView.as_view(), name='request_access')

    ### NOTE: Password reset views are mapped in the dfo_sci_dm_site urls.py file. Views are still in the Accounts app views.py

]
