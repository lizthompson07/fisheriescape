from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'shared_models'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('close_no_refresh/', views.CloserNoRefreshTemplateView.as_view(), name="close_me_no_refresh"),

    # SECTION #
    ###########
    path('section/<int:pk>/update/', views.SectionUpdateView.as_view(), name="section_edit"),
    path('section/<int:pk>/delete/', views.SectionDeleteView.as_view(), name="section_delete"),
    path('section/new/', views.SectionCreateView.as_view(), name="section_new"),

    # DIVISION #
    ############
    path('division/new/', views.DivisionCreateView.as_view(), name="division_new"),

    # DIVISION #
    ############
    path('branch/new/', views.BranchCreateView.as_view(), name="branch_new"),

]
