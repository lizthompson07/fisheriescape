from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'bugs'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),
    path('list/', views.BugListView.as_view(), name ="bug_list" ),
    path('list/<int:application>/', views.BugListView.as_view(), name ="bug_list_4_app" ),
    path('<int:application>/new/', views.BugCreateView.as_view(), name ="bug_create" ),
    path('<int:pk>/view/', views.BugDetailView.as_view(), name ="bug_detail" ),
    path('<int:pk>/resolve/', views.bug_resolved, name ="resolve_bug" ),
    # path('<int:application>/<int:pk>/popup-view/', views.BugDetailView.as_view(), name ="bug_detail_popup" ),
    path('<int:pk>/edit/', views.BugUpdateView.as_view(), name ="bug_edit" ),
    path('<int:pk>/delete/', views.BugDeleteView.as_view(), name ="bug_delete" ),

]
