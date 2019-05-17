from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'publications'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.PublicationsListView.as_view(), name="index"),

    #PUBLICATIONS
    path('new/', views.PublicationCreateView.as_view(), name="pub_new"),
    path('<int:pk>/view', views.PublicationDetailView.as_view(), name="pub_detail"),
    path('publications/<int:pk>/edit', views.PublicationUpdateView.as_view(), name="pub_edit"),
    path('publications/<int:pk>/delete', views.PublicationDeleteView.as_view(), name="pub_delete"),
    path('publications/<int:pk>/submit', views.PublicationSubmitUpdateView.as_view(), name="pub_submit"),

    # Theme #
    #########
    path('theme/new/', views.ThemeCreateView.as_view(), name="new_theme"),
    path('<int:publications>/theme/new/', views.ThemeLookupCreateView.as_view(), name="new_theme_lookup"),
    path('<int:publications>/humancomponents/new/', views.HumanLookupCreateView.as_view(), name="new_human_lookup"),

]
