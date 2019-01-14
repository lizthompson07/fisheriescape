from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'projects'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),

    # PROJECTS #
    ############
    path('my-list/', views.MyProjectListView.as_view(), name="my_project_list"),
    path('projects/', views.ProjectListView.as_view(), name="project_list"),
    path('projects/new/', views.ProjectCreateView.as_view(), name="project_new"),
    path('projects/<int:pk>/view', views.ProjectDetailView.as_view(), name="project_detail"),
    path('projects/<int:pk>/edit', views.ProjectUpdateView.as_view(), name="project_edit"),
    path('projects/<int:pk>/delete', views.ProjectDeleteView.as_view(), name="project_delete"),

    # STAFF #
    #########
    path('project/<int:project>/staff/new/', views.StaffCreateView.as_view(), name="staff_new"),
    path('staff/<int:pk>/edit/', views.StaffUpdateView.as_view(), name="staff_edit"),
    path('staff/<int:pk>/delete/', views.staff_delete, name="staff_delete"),

    # Collaborator #
    ################
    path('project/<int:project>/collaborator/new/', views.CollaboratorCreateView.as_view(), name="collab_new"),
    path('collaborator/<int:pk>/edit/', views.CollaboratorUpdateView.as_view(), name="collab_edit"),
    path('collaborator/<int:pk>/delete/', views.collaborator_delete, name="collab_delete"),

]
