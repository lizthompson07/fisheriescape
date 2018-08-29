from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [


    path('login/', views.UserLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('activate/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('resend-verification-email/<str:email>', views.resend_verification_email, name='resend_verification_email'),
    path('verified/', views.account_verified, name='verified'),
    path('logout/', auth_views.logout, name='logout', kwargs={
        'next_page':'/',
        }),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='account'),
    path('users/change-password/', views.change_password, name='change_password'),
    path('account-request/', views.account_request, name='account_request'),
    path('login_required/', auth_views.login, kwargs={
        'extra_context': {
            'message': "You must be logged in to access this page",
            }
        }),

    ### NOTE: Password reset views are mapped in the glf_sci_site urls.py file. Views are still in the Accounts app views.py

    

]
