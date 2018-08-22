from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [


    path('login/', auth_views.login, name='login'),
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
]
