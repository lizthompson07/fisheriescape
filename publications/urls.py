from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'publications'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.ProjectListView.as_view(), name="index"),

    # Projects
    path('new/', views.ProjectCreateView.as_view(), name="prj_new"),
    path('<int:pk>/view', views.ProjectDetailView.as_view(), name="prj_detail"),
    path('publications/<int:pk>/edit', views.ProjectUpdateView.as_view(), name="prj_edit"),
    path('publications/<int:pk>/delete', views.ProjectDeleteView.as_view(), name="prj_delete"),
    path('publications/<int:pk>/submit', views.ProjectSubmitUpdateView.as_view(), name="prj_submit"),

    # Lookups #
    #########
    path('delete/<str:lookup>/<int:project>/<int:theme>', views.lookup_delete, name="lookup_delete"),
    path('<int:project>/<str:lookup>/new_lookup/', views.ChoiceAddView.as_view(), name="lookup_add"),
    path('<int:project>/<str:lookup>/new_text/', views.TextAddView.as_view(), name="text_add"),

]
