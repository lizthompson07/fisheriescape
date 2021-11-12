from django.urls import path

from . import views

app_name = 'accounts'


urlpatterns = [
    path('denied/', views.access_denied, name='denied_access'),
    path('denied/<str:message>/', views.access_denied, name='denied_access'),
    path('login_required/', views.UserLoginView.as_view(), name='login_required'),

    # main login/logout pages
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    # azure
    path('azure-login/', views.sign_in, name='azure_login'),  # used to access the MZ Azure AD login page
    path('callback/', views.callback, name='callback'),  # used to finalize the authentication from MS Azure AD
    # callback for non-azure authentication
    path('regular-callback/<str:uidb64>/<str:token>/', views.CallBack.as_view(), name='regular_callback'),

    # sign up pages
    path('signup/', views.signup, name='signup'),
    path('activate/<str:uidb64>/<str:token>', views.activate, name='activate'),  # to activate account
    path('resend-activation-email/', views.resend_activation_email, name='resend_activation_email'),  # to activate account


    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),

    path('request-access/', views.RequestAccessFormView.as_view(), name='request_access'),

]
